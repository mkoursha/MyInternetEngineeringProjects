"""Flask Login Example and instagram fallowing find"""

from flask import Flask, url_for, render_template, flash, request, redirect, session,logging,request
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
app.config['UPLOAD_FOLDER'] = './static/images/Uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

class User(db.Model):
    """ Create user table"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(80))
    password = db.Column(db.String(80))

	
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
		
class Product(db.Model):
    """ Create product table"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    productname = db.Column(db.String(80), unique=True)
    productmedia = db.Column(db.String(80))
    tags = db.Column(db.String(100))
    caption = db.Column(db.String(100))
    owner = db.Column(db.Integer)
    store = db.Column(db.Integer)


    def __init__(self, productname, productmedia, owner, store):
        self.productname = productname
        self.productmedia = productmedia
        self.owner = owner
        self.store=store

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True)
    city = db.Column(db.String(80))
    owner = db.Column(db.Integer)
	
    def __init__(self, name, city, owner):
        self.name = name
        self.city = city
        self.owner = owner

class Comment(db.Model):
    """Create Comments table"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.String(80))
    pid = db.Column(db.Integer)
    msg= db.Column(db.String(80), nullable=False)

    def __init__(self, productid, userid, msg):
        self.pid = productid
        self.uid = userid
        self.msg = msg

class Like(db.Model):
    """Create Like table"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.String(80))
    pid = db.Column(db.Integer)
	
    def __init__(self, productid, userid):
        self.pid = productid
        self.uid = userid
		
@app.route('/', methods=['GET', 'POST'])
def home():
    """ Session control"""
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        return render_template('home.html', user=session['username'])

@app.route('/makestore', methods=['POST', 'GET'])
def makestore():
    if request.method == 'GET':
        return render_template('make_new_store.html')
    else:
        x = db.session.query(User).filter(User.username==session['username']).first()
        if x is not None:
            data = db.session.query(Store).filter(Store.name==request.form['name']).first()
            if data is not None:
                flash('store with %s name aleady exists' % (request.form['name']))
                return render_template('make_new_store.html')
            new_store=Store(name=request.form['name'], city=request.form['email'], owner=x.id)
            db.session.add(new_store)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            return redirect(url_for('logout'))

@app.route('/addproduct/<sname>', methods=['POST', 'GET'])
def addproduct(sname):
    if request.method == 'GET':
        return render_template('add_new_product.html', store=sname)
    else:
        x = db.session.query(User).filter(User.username==session['username']).first()
        if x is not None:
            data = db.session.query(Store).filter(Store.owner==x.id, Store.name==sname).first()
            datapro = db.session.query(Product).filter(Product.owner==x.id, Product.store==data.id, Product.productname==request.form['name']).first()
            if datapro is not None:
                flash('store with %s name aleady contains a product %s' % (data.name, request.form['name']))
                return render_template('add_new_product.html', store=data.name)
            if 'avatar' not in request.files:
                flash('NO file part')
                return redirect(url_for('addproduct', sname=data.name))               
            f = request.files['avatar']
            if f.filename == '':
                flash('plz select a media')
                return redirect(url_for('addproduct', sname=data.name))             
            new_product=Product(productname=request.form['name'], productmedia=f.filename, owner=x.id, store=data.id)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
            if request.form['tag'] != '':
                new_product.tags = request.form['tag']
            else:
                new_product.tags = '-'
            if request.form['caption'] != '':
                new_product.caption = request.form['caption']
            else:
                new_product.caption = '-'
            db.session.add(new_product)
            db.session.commit()
            return redirect(url_for('productpage', storename=data.name))
        else:
            return redirect(url_for('logout'))	

@app.route('/user_store')
def user_store():
    name = session['username']
    x = db.session.query(User).filter(User.username==name).first()
    if x is not None:
        stre = db.session.query(Store).filter(Store.owner==x.id).all()
        return render_template('user_store.html', store=stre, user=session['username'], count=len(stre))
    else:
        return redirect(url_for('logout'))

@app.route('/productpage/<storename>')
def productpage(storename):
    name = session['username']
    x = db.session.query(User).filter(User.username==name).first()
    if x is not None:
        stre = db.session.query(Store).filter(Store.owner==x.id, Store.name==storename).first()
        pro = db.session.query(Product).filter(Product.owner==x.id, Product.store==stre.id).all()
        return render_template('productpage.html', product=pro, user=session['username'], store=stre.name, count=len(pro))
    else:
        return redirect(url_for('logout'))

@app.route('/productprofile/<produc>', methods=['GET', 'POST'])
def productprofile(produc):
    if request.method == 'GET':
        name = session['username']
        x = db.session.query(User).filter(User.username==name).first()
        produc = db.session.query(Product).filter(Product.productname==produc).first()
        if x is not None and produc is not None:
            comment = db.session.query(Comment).filter(Comment.pid == produc.id).all()
            like = db.session.query(Like).filter(Like.pid == produc.id).all()
            stre = db.session.query(Store).filter(Store.id == produc.store).first()
            owner = db.session.query(User).filter(User.id == produc.owner).first()
            is_owner_or_not = 1 if x.id == produc.owner else 0
            like_by_user = db.session.query(Like).filter(Like.pid == produc.id, Like.uid==name).first()
            isliked_or_not = 1 if like_by_user is not None else 0
            return render_template('productprofile.html', is_owner=is_owner_or_not, product=produc, user=owner, store=stre, comments=comment, count_comments=len(comment), likes=len(like), isliked_or_not=isliked_or_not)
        else:
            return redirect(url_for('home'))
    else:
        pro_msg = produc+'@#$'+request.form['name']
        return redirect(url_for('savecomment', commentedproduct=pro_msg))


@app.route('/savecomment/<commentedproduct>')
def savecomment(commentedproduct):
    commentedproduct, msg = commentedproduct.split('@#$')
    product = db.session.query(Product).filter(Product.productname == commentedproduct).first()
    if product is not None:
        if msg != '':
            new_c = Comment(productid=product.id, userid=session['username'], msg=msg)
            db.session.add(new_c)
            db.session.commit()
            return redirect(url_for('productprofile', produc=product.productname))
        return redirect(url_for('productprofile', produc=product.productname))
    return redirect(url_for('home'))

@app.route('/storesproductpage/<s_name>')
def storesproductpage(s_name):
    name = session['username']
    x = db.session.query(User).filter(User.username==name).first()
    if x is not None:
        stre = db.session.query(Store).filter(Store.name==s_name).first()
        pro = db.session.query(Product).filter(Product.store==stre.id).all()
        return render_template('storesproductpage.html', product=pro, store=stre.name, count=len(pro))
    else:
        return redirect(url_for('logout'))

@app.route('/showLikes/<product>')
def showLikes(product):
    name = session['username']
    x = db.session.query(User).filter(User.username==name).first()
    produc = db.session.query(Product).filter(Product.productname==product).first()
    if x is not None and produc is not None:
        like = db.session.query(Like).filter(Like.pid == produc.id).all()
        stre = db.session.query(Store).filter(Store.id == produc.store).first()
        owner = db.session.query(User).filter(User.id==produc.owner).first()
        return render_template('showLikes.html', product=produc, user=owner, store=stre, count_likes=len(like), likes=like)
    else:
        return redirect(url_for('home'))
@app.route('/delete/<target>')
def delete(target):
    return render_template('deleteObj.html', obj=target)

@app.route('/like/<product>')
def like(product):
    name = session['username']
    x = db.session.query(User).filter(User.username==name).first()
    produc = db.session.query(Product).filter(Product.productname==product).first()
    like = db.session.query(Like).filter(Like.pid == produc.id, Like.uid==name).first()
    if like is not None:
        db.session.delete(like)
        db.session.commit()
    else:
        l = Like(userid=name, productid=produc.id)
        db.session.add(l)
        db.session.commit()
    return redirect(url_for('productprofile', produc=product))

@app.route('/deleteobj/<object>')
def deleteobj(object):
    user = db.session.query(User).filter(User.username==session['username']).first()
    if user is not None:
        obj = db.session.query(Store).filter(Store.name==object).first()
        if obj is not None:
            products = db.session.query(Product).filter(Product.store==obj.id).all()
            for pro in products:
                c = db.session.query(Comment).filter(Comment.pid==pro.id).all()
                for comm in c:
                    db.session.delete(comm)
                    db.session.commit()    
                l = db.session.query(Like).filter(Like.pid==pro.id).all()
                for lik in l:
                    db.session.delete(lik)
                    db.session.commit()  
                db.session.delete(pro)
                db.session.commit()
            db.session.delete(obj)
            db.session.commit()
            return redirect(url_for('home'))
        obj = db.session.query(Product).filter(Product.productname==object).first()
        if obj is not None:
            c = db.session.query(Comment).filter(Comment.pid==obj.id).all()
            for comm in c:
                db.session.delete(comm)
                db.session.commit()    
            l = db.session.query(Like).filter(Like.pid==obj.id).all()
            for lik in l:
                db.session.delete(lik)
                db.session.commit()
            db.session.delete(obj)
            db.session.commit()
            return redirect(url_for('home'))
        flash('there is no object with specified features')
        return redirect(url_for('delete', target=object))
@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        name = session['username']
        x = db.session.query(User).filter(User.username==name).first()
        if x is not None:
            target = request.form['name']
            if target != '':
                stre = db.session.query(Store).filter(Store.name.like("%{}%".format(target))).first()
                if stre is not None:
                    pro = db.session.query(Product).filter(Product.store ==stre.id, Product.productname.like("%{}%".format(target)) | Product.tags.like("%{}%".format(target)) | Product.caption.like("%{}%".format(target))).all()
                    if len(pro) != 0:
                        msg = "All posible results for products of store {}".format(stre.name)
                        return render_template('searchresult.html', headermsg=msg, store=[], product=pro, count=len(pro), prod=1)
                    msg = "All posible results for store name {}".format(stre.name)
                    stre = [stre]
                    return render_template('searchresult.html', headermsg=msg, store=stre, product=[], count=1, prod=0)
                pro = db.session.query(Product).filter(Product.productname.like("%{}%".format(target)) |Product.tags.like("%{}%".format(target)) | Product.caption.like("%{}%".format(target))).all()
                msg = "All posible products"
                return render_template('searchresult.html', headermsg=msg, store=[], product=pro, count=len(pro), prod=1)
            return redirect(url_for('home')) 
        else:
            return redirect(url_for('logout'))
    return redirect(url_for('home'))
		
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login Form"""
    if request.method == 'GET':
        return render_template('login.html')
    else:
        name = request.form['your_name']
        passw = request.form['your_pass']
        try:
            data = User.query.filter_by(username=name, password=passw).first()
            if data is not None:
                session['username'] = name
                session['logged_in'] = True
                return redirect(url_for('home'))
            else:
                flash('username or password is not correct')
                return redirect(url_for('login'))
        except:
            flash('Incorrect Login')
            return redirect(url_for('login'))

@app.route('/register/', methods=['GET', 'POST'])
def register():
    """Register Form"""
    if request.method == 'POST':
        data = db.session.query(User).filter(User.username==request.form['name']).first()
        if data is not None:
            flash('username already exists')
            return render_template('register.html')
        else:
            new_user = User(username=request.form['name'], email=request.form['email'], password=request.form['pass'])
            db.session.add(new_user)
            db.session.commit()
            return render_template('login.html')
    return render_template('register.html')

@app.route("/logout")
def logout():
	"""Logout Form"""
	session['logged_in'] = False
	return redirect(url_for('home'))

if __name__ == '__main__':
	app.debug = True
	db.create_all()
	app.secret_key = "123"
	app.run()
	
