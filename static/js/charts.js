google.charts.load('current', {packages: ['corechart', 'bar']});

// Draw Graph
function drawBarGraph(queryId, title, subtitle, columns, data) {
    let graphDockingLocation = queryId;
    let footerId = `${queryId}-footer`;
    let footerTextId = `${queryId}-footer-text`;

    data.forEach(record => {
        for (let i = 0; i < record.length; i++) {
            if (i > 0)
                record[i] = parseFloat(record[i]);
        }
    });

    console.log(data);

    // Add Columns as the first element.
    data.splice(0, 0, columns);
    let dataforGraph = google.visualization.arrayToDataTable(data);

    // Options
    let options = {
        chart: {
            title: title,
            subtitle: subtitle,
        },
        bars: 'vertical',
        vAxis: {format: 'decimal'},
        height: 400,
        colors: ['#1b9e77', '#d95f02', '#7570b3']
    };

    let chart = new google.charts.Bar(document.getElementById(graphDockingLocation));
    chart.draw(dataforGraph, google.charts.Bar.convertOptions(options));
}

// Pie chart
function drawPieChart(queryId, title, subtitle, columns, data) {
    console.log('Drawing Pie chart');

    data.forEach(record => record[1] = parseInt(record[1]));
    console.log(data);

    let graphDockingLocation = queryId;
    let footerId = `${queryId}-footer`;
    let footerTextId = `${queryId}-footer-text`;

    let options = {
        title: title,
        pieHole: 0.4,
        // is3D: true,
        pieSliceText: 'value',
        height: 400,
        chartArea: {left: 20, top: 20, width: '100%', height: '100%'}
    };

    data.splice(0, 0, columns);
    var dataforGraph = google.visualization.arrayToDataTable(data);

    var chart = new google.visualization.PieChart(document.getElementById(graphDockingLocation));
    chart.draw(dataforGraph, options);
}