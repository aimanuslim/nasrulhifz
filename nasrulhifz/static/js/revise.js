$(document).ready(function ()
    {
        $('img[usemap]').mapster({
            selected: true,
            mapKey: 'part',
            fillColor: 'FF0000',
            fillOpacity: '1.0'
        });

    });


    document.addEventListener( 'DOMContentLoaded', function () {
         new Splide( '#image-slider', {
         } ).mount();

    } );