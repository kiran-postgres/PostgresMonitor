function createRow(items) {
    let section = document.createElement('section');

    let containerFluid = document.createElement('div');
    containerFluid.className = 'container-fluid';

    let jumbotron = document.createElement('div');
    jumbotron.className = 'jumbotron';

    let row = document.createElement('div');
    row.className = 'row clearfix';

    items.forEach(item => {
        let card = createCard(item['queryId'], item['heading'], item['caption'], item['cardWidth']);
        row.appendChild(card);
    });

    jumbotron.appendChild(row);
    containerFluid.appendChild(jumbotron);
    section.appendChild(containerFluid);

    return section;
}

/**
 *
 * @param queryId - Unique ID of the query that will be executed. This comes from
 *                  backend.
 * @param heading - Heading of the table.
 * @param captionText - Any Caption to be displayed.
 * @param cardWidth - This controls width of the table (This is Bootstrap class name like COL-6, COL-12, etc).
 */
function createCard(queryId, heading, captionText, cardWidth) {
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
    table.id = `${queryId}-table`;

    cardBody.append(caption, table);

    // Card footer
    let cardFooter = document.createElement('div');
    cardFooter.className = 'card-footer';
    cardFooter.id = `${queryId}-table-footer`;

    let footerText = document.createElement('span');
    footerText.id = `${queryId}-table-footer-text`;

    cardFooter.appendChild(footerText);

    card.append(cardHeader, cardBody, cardFooter);
    cardWrapper.append(card);

    return cardWrapper;
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
    console.log('Going to fetch data for ' + link);
    let response = await fetch(link);
    let data = await response.json();
    return data;
}

