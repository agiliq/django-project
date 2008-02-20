 
 /*Handle the project details page.*/
 $(document).ready(function() {
    $('#inviteform').hide();
    $('#taskform').hide();
    
    
    $('#inviteshow').click(function(){
        $('#inviteform').show('slow');
        $('#taskform').hide('fast');
        });
    $('#taskshow').click(function(){
        $('#taskform').show('slow');
        $('#inviteform').hide('fast');
        });
    //Hide controls on tasks
    $('td.taskcontrol').hide();
    $('tr.taskrow').mouseover(function(){
            $(this).children().filter('.taskcontrol').show()
        });
    $('table').mouseout(function(){
            console.log(this)
            $(this).children().children().children().filter('.taskcontrol').hide()
        });
    
 });
 
 $(document).ready(function() {
    $('.taskrowdetail').hide()
    $('.showtaskdetails').click(function(){
        $(this).parent().parent().parent().children().filter('.taskrowdetail').toggle()
        $(this).parent().parent().parent().children().filter('.taskrowdetail').toggle()
        })
     });
 