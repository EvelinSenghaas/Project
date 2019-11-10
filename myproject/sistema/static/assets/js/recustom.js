$('#provincias').change(function() {
    var pv =document.getElementById("provincias").value;
    console.log('oliii')
    $.ajax({
        url: '/sistema/localidadesList',
        data: {
            'provincias': pv,
        },
        dataType: 'json',
        success: function(data) {
            var html = "";
            for (var i = 0; i < data.length; i++) {
                html += "<option value='" + data[i].id_localidad + "'>" + data[i].localidad + "</option>";
            }
            $('#select-localidades').html(html);
        }
    })
});

$('#select-localidades').change(function() {
    var lc = document.getElementById("select-localidades").value;
    console.log(lc)
    console.log('que onda mondonga')
    $.ajax({
        url: '/sistema/barriosList',
        data: {
            'localidad': lc,
        },
        dataType: 'json',
        success: function(data) {
            var html = "";
            for (var i = 0; i < data.length; i++) {
                html += "<option value='" + data[i].id_barrio + "'>" + data[i].barrio + "</option>";
            }
            $('#select-barrio').html(html);
        }
    })
});

