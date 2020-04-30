$(document).ready(function() {
    $('#tbl').hide();
    $('#select-all').click(function(event) {
        var t = $('#tabla-miembros').DataTable();
        $('#1').remove();
        if(this.checked) { // Iterate each checkbox
            $('#lista').empty();
            t.column( 2 ).data().each( function ( value, index ) {
                t.cell(index,2).data(value.replace('input','input checked')); 
                var aux = value.replace('input','input id=id'+ index );
                $('#oculto').append(aux);
                var val = $('#id'+index).val();
                var html = "";
                html += "<option selected name='lista[]' value=" + val + ">" + val + "</option>";
                $('#lista').append(html);
                $('#id'+index).remove();
            });
        }
        else {
            t.column( 2 ).data().each( function ( value, index ) {
                t.cell(index,2).data(value.replace('input checked','input')); 
            });
            $('#lista').empty();
        }
    });

});