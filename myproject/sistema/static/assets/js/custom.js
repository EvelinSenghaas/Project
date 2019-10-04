$(document).ready(function(){
    fecha= new Date($(".f_nac").val());
    fecha_hoy=new Date();
    dayDiff=Math.floor(fecha_hoy-fecha)/(1000*60*60*24*365);
    edad= parseInt(dayDiff);
    $(".edad").text(edad);
    //alert($(".f_nac").val());


});