 $(document).ready(function() {
    $('.taskrowdetail').hide()
    $('.showtaskdetails').click(function(){
        $(this).parent().parent().parent().children().filter('.taskrowdetail').toggle()
        })
     });
 
  $(document).ready(function() {
    $('#subtaskform').hide();
    $('#itemform').hide();
    $('#noteform').hide();
    
    $('#notes').hide();
    $('#itemformshow').click(
        function(){
            $('#itemform').show('slow');
            $('#noteform').hide();
            $('#subtaskform').hide();
            return false;
        }
        );
    $('#taskformshow').click(
        function(){
            $('#subtaskform').show('slow');
            $('#itemform').hide();
            $('#noteform').hide();
            return false;
        }
        );
    $('#shownotes').click(
        function(){
            $(this).toggle(
                //Todo
                function(){$(this).html('Show notes')},
                function(){$(this).html('Hide notes')}
                
            )
            $('#notes').toggle('slow');
            return false;
        }
        );
    $('#shownotesform').click(
        function(){
            $('#noteform').show('slow');
            $('#subtaskform').hide();
            $('#itemform').hide();
            return false;
        }
    )
    toggleform();
 });