$('#id_provincia').change(function() {
    var pv =document.getElementById("id_provincia").value;
    $.ajax({
        url: '/sistema/localidadesList',
        data: {
            'provincia': pv,
        },
        dataType: 'json',
        success: function(data) {
            var html = "";
            html += "<option value=''>-------------------</option>";
            for (var i = 0; i < data.length; i++) {
                html += "<option value='" + data[i].id_localidad + "'>" + data[i].localidad + "</option>";
            }
            $('#id_localidad').html(html);
            var html = "";
            $('#id_barrio').html(html);
        }
    })
});

$('#id_localidad').change(function() {
    var lc = document.getElementById("id_localidad").value;
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
            $('#id_barrio').html(html);
        }
    })
});

