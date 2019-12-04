$('#sexo').change(function() {
    var sx = $(this).val();
    console.log(sx);
    $.ajax({
        url: '/sistema/sexoList',
        data: {
            'mb': sx,
        },
        dataType: 'json',
        success: function(data) {
            var html = "";
            console.log('wenas y wenardas');
            console.log(data.length);
            $('#select-miembro').html("");
            for (var i = 0; i < data.length; i++) {
                html += "<option value=" + data[i].dni + ">" + data[i].apellido +", "+data[i].nombre + "</option>";
            }
            $('#select-miembro').append(html);
        }
    })
});