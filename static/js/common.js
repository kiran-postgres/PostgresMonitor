function createRow(item) {
    let section = document.createElement('section');

    let containerFluid = document.createElement('div');
    containerFluid.className = 'container-fluid';

    let jumbotron = document.createElement('div');
    jumbotron.className = 'jumbotron';

    if (item['table-bootstrap-class'] === 'col-6' &&
        item['graph-required'] === 'Y' &&
        item['graph-bootstrap-class'] === 'col-6') {

        let row = document.createElement('div');
        row.className = 'row clearfix';

        let tableCard = createCard(item['queryId'], 'table', item['heading'], item['caption'], item['table-bootstrap-class']);
        row.appendChild(tableCard);

        let graphCard = createCard(item['queryId'], 'graph', item['heading'], item['caption'], item['graph-bootstrap-class']);
        row.appendChild(graphCard);

        jumbotron.appendChild(row);
        containerFluid.appendChild(jumbotron);
        section.appendChild(containerFluid);

        return section;
    }

    // Create a place holder for Table Data
    let tableRow = document.createElement('div');
    tableRow.className = 'row clearfix';

    let tableCard = createCard(item['queryId'], 'table', item['heading'], item['caption'], item['table-bootstrap-class']);
    tableRow.appendChild(tableCard);
    jumbotron.appendChild(tableRow);

    if (item['graph-required'] === 'Y') {
        let graphRow = document.createElement('div');
        graphRow.className = 'row clearfix my-5';

        let graphCard = createCard(item['queryId'], 'graph', item['heading'], item['caption'], item['graph-bootstrap-class']);
        graphRow.appendChild(graphCard);
        jumbotron.appendChild(graphRow);
    }

    containerFluid.appendChild(jumbotron);
    section.appendChild(containerFluid);

    return section;
}

/**
 *
 * @param queryId - Unique ID of the query that will be executed. This comes from
 *                  backend.
 * @param type - Either 'table' or 'graph'
 * @param heading - Heading of the table.
 * @param captionText - Any Caption to be displayed.
 * @param cardWidth - This controls width of the table (This is Bootstrap class name like COL-6, COL-12, etc).
 */
function createCard(queryId, type, heading, captionText, cardWidth) {
    let cardWrapper = document.createElement('div');
    cardWrapper.className = cardWidth;

    let card = document.createElement('div');
    card.className = 'card rounded';

    // Card header
    let cardHeader = document.createElement('div');
    cardHeader.className = 'card-header';

    let icons = document.createElement('div');
    icons.className = 'icons';

    let h3 = document.createElement('h3');
    h3.innerText = heading;

    icons.appendChild(h3);
    cardHeader.appendChild(icons);

    // Card body
    let cardBody = document.createElement('div');
    cardBody.className = 'card-body';

    let caption = document.createElement('p');
    caption.className = 'card-text';
    caption.innerText = captionText;

    let table = document.createElement('div');
    table.id = `${queryId}-${type}`;

    cardBody.append(caption, table);

    // Card footer
    let cardFooter = document.createElement('div');
    cardFooter.className = 'card-footer';
    cardFooter.id = `${queryId}-${type}-footer`;

    let footerText = document.createElement('span');
    footerText.id = `${queryId}-${type}-footer-text`;

    cardFooter.appendChild(footerText);

    card.append(cardHeader, cardBody, cardFooter);
    cardWrapper.append(card);

    return cardWrapper;
}


function executeQueries(queries) {
    let uniqueQueryIds = Object.keys(queries);
    uniqueQueryIds.forEach(id => executeQuery(id, ''));
}

function executeQuery(queryId, parameters, link = null, dataTableDisplayFlag = true) {
    if (link === null)
        link = queryExecutionLink + queryId + parameters;

    // Target Table ID
    let tableId = queryId + '-table';
    let tableFooter = `${queryId}-table-footer`;
    let tableFooterText = `${queryId}-table-footer-text`;

    fetchRemoteData(link).then((jsonData) => {
        if (jsonData.status === 'success') {
            // Remove existing Data in the table
            while (document.getElementById(`${tableId}`).children.length > 0)
                document.getElementById(`${tableId}`).firstChild.remove();

            let table = createTable(jsonData.data.columns, jsonData.data.records, tableId + '-temp');
            document.getElementById(`${tableId}`).appendChild(table);

            // Make it a Data table based on the flag. Default is True.
            if (dataTableDisplayFlag) {
                $(`#${tableId}-temp`).DataTable({
                    responsive: true,
                    "pageLength": 10
                });
            }

            if (queries[queryId]['graph-required'] === 'Y') {
                let graphId = queryId + '-graph';

                switch (queries[queryId]['graph-type']) {
                    case 'pie-chart':
                        drawPieChart(graphId, 'Database Sizes', null, jsonData.data.columns, jsonData.data.records);
                        break;

                    case 'bar-graph':
                        drawBarGraph(graphId, 'Database Sizes', null, jsonData.data.columns, jsonData.data.records);
                        break;
                }
            }

            document.getElementById(tableFooterText).innerText = `${jsonData.data.records.length} records fetched`;
            document.getElementById(tableFooter).className = 'card-footer alert alert-success alert-dismissible';
        } else {
            // If there is any problem with the Query, show the error message.
            let errorMessage = `There is a problem executing Query ID: ${queryId}.\n`
            document.getElementById(tableFooterText).innerText = errorMessage + jsonData.data;
            document.getElementById(tableFooter).className = 'card-footer alert alert-danger alert-dismissible';
        }
    }).catch(e => {
        // If there is any problem with http link, or with fetching resources, show the error message.
        document.getElementById(tableFooterText).innerText = e;
        document.getElementById(tableFooter).className = 'card-footer alert alert-danger alert-dismissible';
    });

    clearFooter(tableFooter, tableFooterText);
}


function createTable(columns, data, id) {
    let table = document.createElement('table');
    table.id = id;
    table.className = 'table table-hover table-striped table-bordered table-responsive';

    // Create table Header
    let thead = document.createElement('thead');
    let header = document.createElement('tr');

    columns.forEach(col => {
        let th = document.createElement('th');
        th.innerText = col;
        header.appendChild(th);
    });

    let usePreTag = false;

    // If there is only one record present, and in the record there is only one column present,
    // Write using 'pre' tags, so that blank spaces are preserved.
    if (data.length === 1 && data[0].length === 1)
        usePreTag = true;

    thead.appendChild(header);
    table.appendChild(thead);

    let tbody = document.createElement('tbody');
    table.appendChild(tbody);

    // Create Table Data rows
    data.forEach(record => {
        let tr = document.createElement('tr');

        record.forEach(cell => {
            let td = document.createElement('td');

            if (usePreTag) {
                // td.innerHTML = '<pre>' + cell + '</pre>';
                td.innerHTML = '<pre class="prettyprint"><code class="language-sql">' + cell + '</code></pre>';
                td.style.background = '#FFFFFF';
                PR.prettyPrint();
            } else
                td.innerText = cell;

            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });

    return table;
}

function clearFooter(footerId, footerTextId) {
    // Remove the Alert, Error Message after five seconds.
    setTimeout(() => {
        document.getElementById(footerId).className = 'card-footer';
        document.getElementById(footerTextId).innerText = '';
        document.getElementById(footerId).style.marginLeft = '0px';
        document.getElementById(footerId).style.marginRight = '0px';
    }, 5000);
}

/**
 * Fetch JSON Data from server.
 *
 * @param link
 * @returns {Promise<any>}
 */
async function fetchRemoteData(link) {
    let response = await fetch(link);
    let data = await response.json();
    return data;
}