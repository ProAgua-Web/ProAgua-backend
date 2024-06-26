const BASE_URL = window.location.origin;
const pontos = BASE_URL + "/api/v1/pontos";

function search(query) {
    const resultContainer = document.getElementById('result-list');
    resultContainer.innerHTML = '';

    fetch(pontos + `?q=${encodeURIComponent(query)}`)
        .then((response) => {
            if (!response.ok) {
                throw new Error('Erro ao acessar a API');
            }
            return response.json();
        })
        .then((data) => {
            data.items.forEach((item) => {
                const edificacao_url = BASE_URL + item.edificacao_url;

                fetch(edificacao_url)
                    .then((response) => {
                        if (!response.ok) {
                            throw new Error('Erro ao acessar a URL da edificação');
                        }
                        return response.json();
                    })
                    .then((edificacao) => {
                        const listItem = document.createElement('li');
                        listItem.className = 'flex';

                        listItem.id = '' + edificacao.codigo;

                        listItem.innerHTML = `
                    <span class="edification_id">${edificacao.codigo}</span>
                    <span class="edification_name">${edificacao.nome}</span>
                    <button class="modal-button" onclick="change_modal_state(this)"><i class="bi bi-three-dots-vertical"></i></button>
                    <div class="flex modal">
                        <a href="" style="color: #525252;">Editar</a>
                        <a href="" style="color: #FC1B44;">Remover</a>
                    </div>
                `;
                        resultContainer.appendChild(listItem);
                    })
                    .catch((error) => {
                        console.error('Erro:', error);
                    });
            });
        })
        .catch((error) => {
            console.error('Erro:', error);
        });
}

search('');