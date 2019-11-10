$('#select-provincia').change(function() {
    var pv = $(this).val();
    console.log('oliii')
    $.ajax({
        url: '/sistema/localidadesList',
        data: {
            'provincia': pv,
        },
        dataType: 'json',
        success: function(data) {
            var html = "";
            for (var i = 0; i < data.length; i++) {
                html += "<option value='" + data[i].id_localidad + "'>" + data[i].localidad + "</option>";
            }
            $('#select-localidad').html(html);
        }
    })
});

$('#select-localidad').change(function() {
    var lc = document.getElementById("select-localidad").value;
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
            $('#select-barrios').html(html);
        }
    })
});

