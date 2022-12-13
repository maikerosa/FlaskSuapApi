from flask import Flask, redirect, url_for, session, request, jsonify, render_template
from flask_oauthlib.client import OAuth



app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

suap = oauth.remote_app(
    'suap',
    consumer_key="sKtxQY8Hg3jeRzG4gPPLK42aMJwzofApwzH1nahp",
    consumer_secret="Hmcjoq2wVDqrSO0UEi9SxlLSUOKTyha7cm9J6HkV4x2Diqc99yKf7Q5K5PnFHLVn42ZZjl6RgHKjowxaXB3h63kftkg7dv7pn1kSzcks2tNhoVvtgeJNpLG2yT2DpG0G",
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




@app.route('/boletins', methods=['GET', 'POST'])
def boletins():
    if 'suap_token' in session:
        if request.method == 'GET':
            periodos_letivos_do_aluno = suap.get('v2/minhas-informacoes/meus-periodos-letivos/')
            ano_letivo = []
            for periodo in periodos_letivos_do_aluno.data:
                if periodo['ano_letivo'] not in ano_letivo:
                    ano_letivo.append(periodo['ano_letivo'])
            ano_letivo.sort(reverse=True)
            me = suap.get('v2/minhas-informacoes/boletim/{ano}/{periodo}'.format(ano=2022, periodo=1))
            return render_template('boletins.html', boletins=me.data, ano=2022, periodo=1, ano_letivo=ano_letivo)
        if request.method == 'POST':
            periodos_letivos_do_aluno = suap.get('v2/minhas-informacoes/meus-periodos-letivos/')
            ano_letivo = []
            for periodo in periodos_letivos_do_aluno.data:
                if periodo['ano_letivo'] not in ano_letivo:
                    ano_letivo.append(periodo['ano_letivo'])
            ano_letivo.sort(reverse=True)
            ano = request.form['ano']
            ano = int(ano)
            periodo = request.form['periodo']
            me = suap.get('v2/minhas-informacoes/boletim/{ano}/{periodo}'.format(ano=ano, periodo=periodo))
            if 'detail' in me.data:
                me.data = None
            return render_template('boletins.html', boletins=me.data, ano=ano, periodo=periodo, ano_letivo=ano_letivo)
    else:
        return render_template('index.html')



@app.route('/app', methods=['GET', 'POST'])
def secret():
    if 'suap_token' in session:
        if request.method == 'GET':
            apps = suap.get('applications/')
            apps = apps.data['results']
        elif request.method == 'POST':
            nome = request.form['name']
            tipo = request.form['client_type']
            grant = request.form['authorization_grant_type']
            redirect = request.form['redirect_uris']

            app = suap.post('applications/', data={
                'name': nome,
                'client_type': tipo,
                'authorization_grant_type': grant,
                'redirect_uris': redirect,
                'username': 'username',
                'email': 'email',
            })
            apps = suap.get('applications/')
            apps = apps.data['results']

        return render_template('secret.html', apps=apps)
    else:
        return render_template('index.html')

@suap.tokengetter
def get_suap_oauth_token():
    return session.get('suap_token')

if __name__ == '__main__':
    app.run()
