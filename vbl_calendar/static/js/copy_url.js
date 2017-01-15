$('document').ready(function(){

    $('#copy_calendar_url').on('click', function(){
        var calendar_url = $(this).attr('calendar_url');

        var $tempInput =  $("<textarea>");
        $("body").append($tempInput);
        $tempInput.val(calendar_url).select();
        document.execCommand("copy");
        $tempInput.remove();
    });

});