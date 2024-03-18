const BASE_URL = "";
const container = document.getElementById("container");

async function getSequenciaColetas(id) {
    let response = await fetch(`${BASE_URL}/api/v1/sequencias/${id}`);
    if (!response.ok) {
        throw new Error(`Erro ao acessar a API: ${response.statusText}`);
    }
    return await response.json();
}

function groupColetaByPonto(coletas) {
    let groups = [];
    let current_group = {
        ponto: coletas[0].ponto_url,
        coletas: []
    };
    
    coletas.forEach((coleta) => {
        if (current_group.ponto != coleta.ponto_url) {
            groups.push(current_group);
            current_group = {
                ponto: coleta.ponto_url,
                coletas: []
            };
        }
        current_group.coletas.push(coleta);
    });

    groups.push(current_group);

    return groups;
}

async function createTableColetas(data) {
    const columns = [
        '-',
        'Ordem',
        'Temperatura',
        'Cloro residual livre',
        'Turbidez',
        'Coliformes totais',
        'Escherichia coli',
        'Cor',
        'Data',
        'Responsável',
        'Status',
        'Editar'
    ];
    const table = document.createElement("table");
    const header_row = document.createElement("tr");
    const body_rows = [];

    // Create table header
    columns.forEach(value => {
        let th = document.createElement('th');
        th.innerText = value.toString();
        header_row.appendChild(th);
    });

    // Create table rows
    for (const coleta of data) {
        // Gerar string com nome dos responsáveis
        let response = await fetch(coleta.responsaveis_url);
        let arr_responsaveis = await response.json();
        let responsaveis = arr_responsaveis.reduce(
            (acc, current_value) => (acc ? acc + ', ' : '') + current_value.username,
            ''
        );

        // Construir linha da tabela
        let row = document.createElement('tr');
        row.innerHTML = `
            <td>${coleta.id}</td>
            <td>${coleta.ordem}</td>
            <td>${coleta.temperatura} ºC</td>
            <td>${coleta.cloro_residual_livre} mg/L</td>
            <td>${coleta.turbidez} uT </td>
            <td>${coleta.coliformes_totais
            ? 'Presença'
            : 'Ausência'}</td>
            <td>${coleta.escherichia
            ? 'Presença'
            : 'Ausência'}</td>
            <td>${coleta.cor}</td>
            <td>${coleta.data}</td>
            <td>${responsaveis}</td>
            <td style="text-align: center;">${coleta.status.status
            ? '<i class="bi bi-check2"></i>'
            : '<i class="bi bi-x"></i>'}
            ${coleta.status.message}
            </td>
            <td>
                <a href="/coletas/${coleta.id}">Editar</a>
            </td>
        `;
        body_rows.push(row);
    };

    table.append(header_row, ...body_rows);
    return table;
}


// Construir tabela de coletas
const id_sequencia = window.location.pathname.split("/sequencias_coletas/")[1];

getSequenciaColetas(parseInt(id_sequencia)).then(sequencia => {
    let grupos = groupColetaByPonto(sequencia.coletas);

    grupos.forEach(grupo => {
        let title = document.createElement('h3');
        if (grupo.ponto) {
            title.innerText = String(grupo.ponto).toString();
        }
        
        createTableColetas(grupo.coletas).then(table => {
            container?.append(title);
            container?.append(table);
        });

    });
});