# -*- coding: utf-8 -*-
"""
    :author: ZFF
    :email: <helloworldzff@163.com>
"""
from flask import jsonify, request, current_app, url_for, g
from flask.views import MethodView
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_, and_, text

from todoism.apis.v1 import api_v1
from todoism.apis.v1.auth import auth_required, generate_token
from todoism.apis.v1.errors import api_abort, ValidationError
from todoism.apis.v1.schemas import user_schema, users_schema, item_schema, items_schema
from todoism.extensions import db
from todoism.models import User, Item


def get_item_body():
    data = request.get_json()
    body = data.get('body')
    if body is None or str(body).strip() == '':
        raise ValidationError('The item body was empty or invalid.')
    return body


class IndexAPI(MethodView):

    @property
    def get(self):
        return jsonify({
            "api_version": "1.0",
            "api_base_url": "http://example.com/api/v1",
            "current_user_url": "http://example.com/api/v1/user",
            "authentication_url": "http://example.com/api/v1/token",
            "item_url": "http://example.com/api/v1/items/{item_id }",
            "current_user_items_url": "http://example.com/api/v1/user/items{?page,per_page}",
            "current_user_active_items_url": "http://example.com/api/v1/user/items/active{?page,per_page}",
            "current_user_completed_items_url": "http://example.com/api/v1/user/items/completed{?page,per_page}",
        })


# 关于登录校验的
class AuthTokenAPI(MethodView):

    # 用户登录
    def post(self):
        data = request.get_json()
        grant_type = data.get('grant_type')
        username = data.get('username')
        password = data.get('password')

        if grant_type is None or grant_type.lower() != 'password':
            return api_abort(code=400, message='The grant type must be password.')

        user = User.query.filter_by(username=username).first()
        if user is None or not user.validate_password(password):
            return api_abort(code=400, message='Either the username or password was invalid.')

        token, expiration = generate_token(user)

        response = jsonify({
            'token': token,
            'token_type': 'Bearer',
            'expires_in': expiration
        })
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Pragma'] = 'no-cache'
        return response


    # 用户退出
    def get(self):
        # logout_user()
        return jsonify(message='Logout success.')


class ItemAPI(MethodView):
    decorators = [auth_required]

    def get(self, item_id):
        """Get item."""
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            return api_abort(403)
        return jsonify(item_schema(item))

    def put(self, item_id):
        """Edit item."""
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            return api_abort(403)
        item.body = get_item_body()
        db.session.commit()
        return '', 204

    def patch(self, item_id):
        """Toggle item."""
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            return api_abort(403)
        item.done = not item.done
        db.session.commit()
        return '', 204

    def delete(self, item_id):
        """Delete item."""
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            return api_abort(403)
        db.session.delete(item)
        db.session.commit()
        return '', 204


class ItemsAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        """Get current user's all items."""
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['TODOISM_ITEM_PER_PAGE']
        pagination = Item.query.with_parent(g.current_user).paginate(page, per_page)
        items = pagination.items
        current = url_for('.items', page=page, _external=True)
        prev = None
        if pagination.has_prev:
            prev = url_for('.items', page=page - 1, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('.items', page=page + 1, _external=True)
        return jsonify(items_schema(items, current, prev, next, pagination))

    def post(self):
        """Create new item."""
        item = Item(body=get_item_body(), author=g.current_user)
        db.session.add(item)
        db.session.commit()
        response = jsonify(item_schema(item))
        response.status_code = 201
        response.headers['Location'] = url_for('.item', item_id=item.id, _external=True)
        return response


'''
# 关于管理员操作账号：增、删、改、查
访问地址 /users
查列表：     /users        get
增：         /users        post

访问地址 /user
查单个：     /user/id      get
改部分字段：  /user/id     patch
删：         /user/id     delete
改全部字段：  /user/id     put
'''
class UsersAPI(MethodView):
    # 增
    def post(self):
        # 1 获取数据
        data = request.get_json()# formargs values
        username = data.get("username")
        password = data.get("password")  # 为真时的结果 if 判断条件 else 为假时的结果（注意，没有冒号）
        telnumber = data.get("telnumber")
        gender = data.get("gender")
        limit = data.get("role_type")
        # print("post 166")
        # print(limit)
        # print("post 166")

        # 2 判断数据合法性和处理数据
        if User.query.filter_by(telnumber=telnumber).first() is not None:
            return jsonify({"msg": '手机号已存在', "response_code": 42000})

        limitValue = 0
        if (limit != None and len(limit)):
            for i in limit:
                limitValue += int(i)

        # 3 往数据库存数据
        user = User(username=username)
        user.set_password(password)
        user.telnumber = telnumber
        user.gender = gender
        user.status = '正常'
        user.type = limitValue
        user.role_type = ','.join(limit)
        db.session.add(user)
        db.session.commit()

        return jsonify(msg="创建成功", response_code=20000)

    # 查列表
    def get(self):
        page = request.args.get('page', 1, type=int)

        # 搜索的条件
        username = request.args.get('username', '', type=str)
        telnumber = request.args.get('telnumber', '', type=str)

        print(username, type(username))
        print(telnumber, type(telnumber))

        # TODO 这里暂时不知道怎么写多条件的or like
        if (username != '' or username is not None) and (telnumber != '' or telnumber is not None):
            pagination = User.query.filter(
                User.status == '正常',
                or_(User.telnumber == telnumber,User.username.like("%" + username + "%") )
            ).paginate(
                page, per_page=current_app.config['TODOISM_ITEM_PER_PAGE'])
        elif (username != '' or username is None) and (telnumber == '' or telnumber is None):
            pagination = User.query.filter(
                User.status == '正常',
                User.username.like("%" + username + "%")
            ).paginate(
                page, per_page=current_app.config['TODOISM_ITEM_PER_PAGE'])
        elif (telnumber != '' or telnumber is not None ) and (username == '' or username is not None):
            print(str(User.query.filter(
                User.status == '正常',
                or_(User.telnumber == telnumber)
            )))
            pagination = User.query.filter(
                User.status == '正常',
                or_(User.telnumber == telnumber)
            ).paginate(
                page, per_page=current_app.config['TODOISM_ITEM_PER_PAGE'])
        else:
            pagination = User.query.filter(
                User.status == '正常'
            ).paginate(
                page, per_page=current_app.config['TODOISM_ITEM_PER_PAGE'])

        users = pagination.items
        current = url_for('.users', page=page, _external=True)
        prev = None
        if pagination.has_prev:
            prev = url_for('.users', page=page - 1, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('.users', page=page + 1, _external=True)
        return jsonify(users_schema(users, current, prev, next, pagination))

class UserAPI(MethodView):
    # decorators = [auth_required]

    def get(self, id):
        query = request.get_json()
        print(query)
        return jsonify(user_schema(g.current_user))

    def patch(self, id):
        '''delete user instead of update data status to 9'''
        # TODO 验证数据的合法性
        user = User.query.get(id=id)
        if user is None:
            return jsonify(msg="参数错误", code=41000)

        # 这里修改数据库
        User.query.filter_by(id=id).update({'status': "已删除"})
        db.session.commit()
        return jsonify(msg='success', code=200)

    def delete(self, id):
        pass

    # 编辑更新账户信息
    def put(self, id):
        data = request.args # get_json() args  values data json

        username = data.get("username")
        telnumber = data.get("telnumber")
        typeValue = data.get("typeValue")
        status = data.get("status")
        gender = data.get("gender")
        password = data.get("password")

        user = User.query.get(id)

        if user is None:
            return jsonify(msg="参数错误", code=41000)

        # 数据整理
        if password is not None:
            user.set_password(password)

        roleTypeConfig = {
            8: '8',
            4: '4',
            2: '2',
            1: '1',
            12: '4, 8',
            10: '8, 2',
            9: '8, 1',
            6: '4, 2',
            5: '4, 1',
            3: '2, 1',
            14: '8, 4, 2',
            13: '8, 4, 1',
            7: '4, 2, 1',
            11: '8, 2, 1',
            15: '8, 4, 2, 1'
        }
        # print(typeValue, type(typeValue))

        user.username = username
        user.telnumber = telnumber
        user.telnumber = telnumber
        user.type = typeValue
        user.role_type = roleTypeConfig[int(typeValue)]
        user.status = status
        user.gender = gender
        user.password = password
        db.session.commit()

        return jsonify({
            'msg': "修改成功",
            'response_code': 2000
        })



class ActiveItemsAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        """Get current user's active items."""
        page = request.args.get('page', 1, type=int)
        pagination = Item.query.with_parent(g.current_user).filter_by(done=False).paginate(
            page, per_page=current_app.config['TODOISM_ITEM_PER_PAGE'])
        items = pagination.items
        current = url_for('.items', page=page, _external=True)
        prev = None
        if pagination.has_prev:
            prev = url_for('.active_items', page=page - 1, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('.active_items', page=page + 1, _external=True)
        return jsonify(items_schema(items, current, prev, next, pagination))


class CompletedItemsAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        """Get current user's completed items."""
        page = request.args.get('page', 1, type=int)
        pagination = Item.query.with_parent(g.current_user).filter_by(done=True).paginate(
            page, per_page=current_app.config['TODOISM_ITEM_PER_PAGE'])
        items = pagination.items
        current = url_for('.items', page=page, _external=True)
        prev = None
        if pagination.has_prev:
            prev = url_for('.completed_items', page=page - 1, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('.completed_items', page=page + 1, _external=True)
        return jsonify(items_schema(items, current, prev, next, pagination))

    def delete(self):
        """Clear current user's completed items."""
        Item.query.with_parent(g.current_user).filter_by(done=True).delete()
        db.session.commit()  # TODO: is it better use for loop?
        return '', 204



api_v1.add_url_rule('/', view_func=IndexAPI.as_view('index'), methods=['GET'])
api_v1.add_url_rule('/oauth/token', view_func=AuthTokenAPI.as_view('token'), methods=['GET', 'POST', 'DELETE'])

api_v1.add_url_rule('/users', view_func=UsersAPI.as_view('users'), methods=['GET', 'POST']) # user表
api_v1.add_url_rule('/user/<int:id>', view_func=UserAPI.as_view('user'), methods=['GET', 'DELETE', 'PATCH', 'PUT']) # user表 有参数的

api_v1.add_url_rule('/user/items', view_func=ItemsAPI.as_view('items'), methods=['GET', 'POST'])
api_v1.add_url_rule('/user/items/<int:item_id>', view_func=ItemAPI.as_view('item'),
                    methods=['GET', 'PUT', 'PATCH', 'DELETE'])
api_v1.add_url_rule('/user/items/active', view_func=ActiveItemsAPI.as_view('active_items'), methods=['GET'])
api_v1.add_url_rule('/user/items/completed', view_func=CompletedItemsAPI.as_view('completed_items'),
                    methods=['GET', 'DELETE'])
