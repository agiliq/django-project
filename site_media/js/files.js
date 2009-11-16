$(document).ready(function(){
 $('.oldrevisions').next().hide()
 $('.oldrevisions').click(function(){
    $(this).next().toggle();
    /*$(this).toggle(function(){$(this)html('Hide Revisions')},
                   function(){$(this)html('Show Revisions')})*/
    });
})