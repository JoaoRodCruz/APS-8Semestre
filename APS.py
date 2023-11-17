from flask import Flask, jsonify, request
import pandas as pd
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

# Inicialização do aplicativo Flask
app = Flask(__name__)

# Configuração do JWT (JSON Web Tokens)
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']
jwt = JWTManager(app)

# Criação de variáveis
valid_tokens = {}
data = pd.read_csv('data/football_wages.csv')

# Autentica um usuário e fornece um token JWT válido
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    # Verifique aqui as credenciais do usuário (exemplo simplificado)
    if username == 'jordan' and password == '654321':
        access_token = create_access_token(identity=username)
        valid_tokens[username] = access_token
        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'message': 'Credenciais inválidas'}), 401

# Invalida o token JWT de um usuário autenticado
@app.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():
    current_user = get_jwt_identity()
    if current_user in valid_tokens:
        del valid_tokens[current_user]
        return jsonify({'message': 'Logout realizado com sucesso'}), 200
    else:
        return jsonify({'message': 'Usuário não autenticado'}), 401


# Exemplo de rota protegida por autenticação JWT
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    return jsonify({'message': 'Rota protegida!'})



# Retorna os dados carregados do arquivo CSV
@app.route('/dados', methods=['GET'])
@jwt_required()  # Esta rota agora exige autenticação JWT
def get_dados_protegido():
    current_user = get_jwt_identity()
    return jsonify(data.to_dict(orient='records'))

# Adiciona novos dados ao arquivo CSV
@app.route('/api/dados', methods=['POST'])
@jwt_required()
def add_dado():
    current_user = get_jwt_identity()
    global data  # Indica que 'data' será usada globalmente nesta função
    new_data = request.get_json()
    new_data_df = pd.DataFrame([new_data])  # Convertendo o novo dado em um DataFrame
    data = pd.concat([data, new_data_df], ignore_index=True)  # Usando o método concat para adicionar o novo dado ao DataFrame existente
    return jsonify({'message': 'Dado adicionado com sucesso!'})

# Atualiza um dado específico do arquivo CSV
@app.route('/api/dados/<int:dado_id>', methods=['PUT'])
@jwt_required()
def update_dado(dado_id):
    current_user = get_jwt_identity()
    data_to_update = request.get_json()
    data.iloc[dado_id] = data_to_update
    return jsonify({'message': 'Dado atualizado com sucesso!'})

# Modifica um dado específico do arquivo CSV
@app.route('/api/dados/<int:dado_id>', methods=['PATCH'])
@jwt_required()
def modify_dado(dado_id):
    current_user = get_jwt_identity()
    data_to_modify = request.get_json()
    data.iloc[dado_id] = {**data.iloc[dado_id], **data_to_modify}
    return jsonify({'message': 'Dado modificado com sucesso!'})

# Deleta um dado específico do arquivo CSV
@app.route('/api/dados/<int:dado_id>', methods=['DELETE'])
@jwt_required()
def delete_dado(dado_id):
    current_user = get_jwt_identity()
    data.drop(index=dado_id, inplace=True)
    return jsonify({'message': 'Dado deletado com sucesso!'})

# Retorna dados paginados do arquivo CSV
@app.route('/dados-paginados', methods=['GET'])
@jwt_required()
def get_dados_paginados():
    current_user = get_jwt_identity()
    page = request.args.get('page', default=1, type=int)
    items_por_pagina = request.args.get('items_por_pagina', default=2, type=int)

    paginated_data = data.iloc[(page - 1) * items_por_pagina:page * items_por_pagina]

    return jsonify(paginated_data.to_dict(orient='records'))

# Execução do aplicativo
if __name__ == '__main__':
    app.run(debug=True)