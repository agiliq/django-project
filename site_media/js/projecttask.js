/*Handle the showing and hiding of task controls. This is for the tasks page. */ 
 $(document).ready(function() {
    $('#taskform').hide();
    $('#taskshow').click(function(){
        $('#taskform').show('slow');
        });
    $('td.taskcontrol').hide();
    $('li.taskrow').mouseover(function(){
            $(this).children().children().children().children().filter('.taskcontrol').show()
            
        });
    $('li.taskrow').mouseout(function(){
            $(this).children().children().children().children().filter('.taskcontrol').hide()
            
        });
 });
 
  
 $(document).ready(function() {
    $('.taskrowdetail').hide()
    $('.showtaskdetails').click(function(){
        $(this).parent().parent().parent().children().filter('.taskrowdetail').toggle();
        return false;
        })
    toggleform();
     });