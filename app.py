from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'uas-dpa'  # Ganti dengan secret key yang lebih aman

api = Api(app)
jwt = JWTManager(app)
db = SQLAlchemy(app)

# Model transaksi
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

# Model kategori transaksi
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Parsing argumen untuk input transaksi
transaction_parser = reqparse.RequestParser()
transaction_parser.add_argument('description', type=str, required=True, help='Description is required')
transaction_parser.add_argument('amount', type=float, required=True, help='Amount is required')
transaction_parser.add_argument('category_id', type=int, required=True, help='Category ID is required')

# Resource untuk transaksi
class TransactionResource(Resource):
    @jwt_required()
    def get(self, transaction_id=None):
        if transaction_id:
            transaction = Transaction.query.get(transaction_id)
            if transaction:
                return {'id': transaction.id, 'description': transaction.description,
                        'amount': transaction.amount, 'category_id': transaction.category_id}
            return {'message': 'Transaction not found'}, 404

        transactions = Transaction.query.all()
        return [{'id': t.id, 'description': t.description, 'amount': t.amount, 'category_id': t.category_id}
                for t in transactions]

    @jwt_required()
    def post(self):
        args = transaction_parser.parse_args()
        transaction = Transaction(description=args['description'], amount=args['amount'], category_id=args['category_id'])
        db.session.add(transaction)
        db.session.commit()
        return {'message': 'Transaction created successfully'}, 201

    @jwt_required()
    def put(self, transaction_id):
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            return {'message': 'Transaction not found'}, 404

        args = transaction_parser.parse_args()
        transaction.description = args['description']
        transaction.amount = args['amount']
        transaction.category_id = args['category_id']
        db.session.commit()
        return {'message': 'Transaction updated successfully'}

    @jwt_required()
    def delete(self, transaction_id):
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            return {'message': 'Transaction not found'}, 404

        db.session.delete(transaction)
        db.session.commit()
        return {'message': 'Transaction deleted successfully'}
    
# Resource untuk kategori transaksi
class CategoryResource(Resource):
    @jwt_required()
    def get(self, category_id=None):
        if category_id:
            category = Category.query.get(category_id)
            if category:
                return {'id': category.id, 'name': category.name}
            return {'message': 'Category not found'}, 404

        categories = Category.query.all()
        return [{'id': c.id, 'name': c.name} for c in categories]

    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Name is required')
        args = parser.parse_args()

        category = Category(name=args['name'])
        db.session.add(category)
        db.session.commit()
        return {'message': 'Category created successfully'}, 201

    @jwt_required()
    def put(self, category_id):
        category = Category.query.get(category_id)
        if not category:
            return {'message': 'Category not found'}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Name is required')
        args = parser.parse_args()

        category.name = args['name']
        db.session.commit()
        return {'message': 'Category updated successfully'}

    @jwt_required()
    def delete(self, category_id):
        category = Category.query.get(category_id)
        if not category:
            return {'message': 'Category not found'}, 404

        db.session.delete(category)
        db.session.commit()
        return {'message': 'Category deleted successfully'}

api.add_resource(CategoryResource, '/categories', '/categories/<int:category_id>')
api.add_resource(TransactionResource, '/transactions', '/transactions/<int:transaction_id>')

if __name__ == '__main__':
    with app.app_context():
       db.create_all()
       app.run(debug=True)
