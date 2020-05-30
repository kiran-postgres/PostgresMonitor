let webServer = 'http://localhost:5000';
let query_map_link = webServer + '/get_query_map';
let queryExecutionLink = 'http://localhost:5000/query_execution/';
let queries = {};

// On Page loading, retrieve the list of queries to be executed and rendered.
window.addEventListener('DOMContentLoaded', (event) => {
    fetchRemoteData(query_map_link).then((data) => {
        queries = data;

        // When a query executes, its results will be rendered in tabular format. This step
        // Creates the place holders / IDs for the table. For each query, there will be a table.
        // For some queries, we would like to generate Graphs too. Based on Queries configuration,
        // this step generates a place holder for graph too!
        generatePlaceHolders(queries);

        // Execute all the Queries
        executeQueries(queries);
    }).catch(e => {
        console.log('Unable to extract queries to be executed from: ' + query_map_link);
    });
});

/**
 *
 * @param queries - A JSON Object with multiple attributes. Attribute name is the unique query id,
 *                  and value will have the following attributes:
 *                  - heading
 *                  - caption
 */
function generatePlaceHolders(queries) {
    let uniqueQueryIds = Object.keys(queries);

    uniqueQueryIds.forEach(id => {
        let item = {};
        item['queryId'] = id;
        item['heading'] = queries[id]['heading'];
        item['caption'] = queries[id]['caption'];
        item['graph-required'] = queries[id]['graph-required'];
        item['graph-type'] = queries[id]['graph-type'];
        item['graph-width'] = queries[id]['graph-width'];
        item['table-width'] = queries[id]['table-width'];

        // Setup Bootstrap class for table. If width is 'half', use 6 columns,
        // Otherwise use 12 columns. Here, each column is Bootstrap column.
        if (item['table-width'] === 'half')
            item['table-bootstrap-class'] = 'col-6';
        else
            item['table-bootstrap-class'] = 'col-12';

        // Graph setup
        if (item['graph-required'] === 'Y') {
            if (item['graph-width'] === 'half')
                item['graph-bootstrap-class'] = 'col-6';
            else
                item['graph-bootstrap-class'] = 'col-12';
        }

        let row = createRow(item);
        document.getElementById('progress-results').appendChild(row);
    });
}

document.getElementById('query-execute-submit-btn')
    .addEventListener('click', (e) => {
    e.preventDefault();
    let sqlText = document.getElementById('query-to-execute').value;
    let url = `${webServer}/execute_custom_sql`;

    let footer = document.getElementById('query-execute-footer');
    let footerText = document.getElementById('query-execute-footer-text');

    document.getElementById('query-to-execute').innerHTML =
        '<pre class="prettyprint"><code class="language-sql">' + sqlText + '</code></pre>';

    let payload = {};
    payload['query'] = sqlText;

    const xhr = new XMLHttpRequest();
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(payload));

    xhr.onload = function () {
        if (this.status === 201) {
            const response = JSON.parse(this.responseText);

            if (response.status === 'success') {
                let jsonData = response.data;
                let tableId = 'query-results-table';

                while (document.getElementById(`${tableId}`).children.length > 0)
                    document.getElementById(`${tableId}`).firstChild.remove();

                let table = createTable(jsonData.columns, jsonData.records, tableId + '-temp');
                document.getElementById(`${tableId}`).appendChild(table);

                $(`#${tableId}-temp`).DataTable({
                    responsive: true,
                    "pageLength": 10
                });

                PR.prettyPrint();

                $('#coll-1').collapse('hide');
                $('#coll-2').collapse('show');
            }

            if (response.status !== 'success') {
                let errorMessage = `There is a problem executing Query.\n`;
                footerText.innerText = errorMessage + response.data;
                footer.className = 'card-footer alert alert-danger alert-dismissible';
                clearFooter('query-execute-footer', 'query-execute-footer-text');
            }
        } else {
            footerText.innerText = 'Unable to fetch data from: ' + `${webServer}/execute_custom_sql`;
            footer.className = 'card-footer alert alert-danger alert-dismissible';
            clearFooter('query-execute-footer', 'query-execute-footer-text');
        }
    };
});


