from flask import Flask, redirect, url_for, session, request, jsonify, render_template
from flask_oauthlib.client import OAuth


app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

suap = oauth.remote_app(
    'suap',
    consumer_key="zeM1RA5ruf5BV9V813h0DPefsVVSem9qWMATV5Na",
    consumer_secret="tHPp565ug8gX4IFPt2pidsmzsrH1xl1w3oLWp1VhZoiZ7bwDdcBjfKqVJHnVQ9MYRucGcS7SSp2Ne9HDcn8OAHLtac3IfczdAwdfgPwFsSXSM9c6kGrX6svTf9ZvfmOg",
    base_url='https://suap.ifrn.edu.br/api/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://suap.ifrn.edu.br/o/token/',
    authorize_url='https://suap.ifrn.edu.br/o/authorize/'
)


@app.route('/')
def index():
    if 'suap_token' in session:
        me = suap.get('v2/minhas-informacoes/meus-dados')
        me_vinculo = me.data['vinculo']
        return render_template('user.html', user=me.data, vinculo=me_vinculo)
    else:
        return render_template('index.html')


@app.route('/login')
def login():
    return suap.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('suap_token', None)
    return redirect(url_for('index'))


@app.route('/login/authorized')
def authorized():
    resp = suap.authorized_response()
    if resp is None or resp.get('access_token') is None:
       return 'Access denied: reason=%s error=%s resp=%s' % (
            request.args['error'],
            request.args['error_description'],
            resp
        )
    session['suap_token'] = (resp['access_token'], '')
    return redirect(url_for('index')) 


@app.route('/boletins')
def boletins():
    if 'suap_token' in session:
        me = suap.get('v2/minhas-informacoes/boletim/{ano}/{periodo}'.format(ano=2022, periodo=1))

        return render_template('boletins.html', boletins=me.data)
    else:
        return render_template('index.html')


@suap.tokengetter
def get_suap_oauth_token():
    return session.get('suap_token')

if __name__ == '__main__':
    app.run()
