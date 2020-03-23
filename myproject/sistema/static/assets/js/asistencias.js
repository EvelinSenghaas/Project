$(document).ready(function() {
    $('#tbl').hide();
    $('#select-all').click(function(event) {
        var t = $('#tabla-miembros').DataTable();
        var info = t.page.info();        
        if(this.checked) { // Iterate each checkbox
            t.column( 2 ).data().each( function ( value, index ) {
                t.cell(index,2).data(value.replace('input','input checked')); 
            });
        }
        else {
            $('#oculto').remove();
            t.column( 2 ).data().each( function ( value, index ) {
                t.cell(index,2).data(value.replace('input checked','input')); 
            });
        }
    });

});