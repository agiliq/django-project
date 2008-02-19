/*The things we need to do for each page.
1. Add a close field button to each form. Add handlers for that.
2. Add validations for each form. Depending on their class.
3. Hide the help text.
4. Make the forms get the css-class when focussed. This helps us give visual clue. Remove class on blur.
5. Attach datepicker, to date fields
*/
 $(document).ready(function(){
    $('legend.collapasble').append(' <a href="#" class="closeform">x</a> ');
    $('.closeform').click(function(){
        $(this).parent().parent().parent().parent().hide();
        });    
    //$('form').validate();
    $('.help_text').hide()
    $('input[@type="text"]').focus(function(){
        $(this).next().filter('.help_text').show();
    })
    $('input[@type="text"]').blur(function(){
        $(this).next().filter('.help_text').hide();
    })
    $('input[@type="text"]').focus(function(){
      $(this).addClass('focusfield');
    });
    $('input[@type="text"]').blur(function(){
      $(this).removeClass('focusfield');
    });
    //$('.datefield').attachDatepicker();
    });
/*Handle the showing and hiding of task controls. This is for the tasks page. */ 
 $(document).ready(function() {
    $('#taskform').hide();
    $('#taskshow').click(function(){
        $('#taskform').show('slow');
        });
    $('td.taskcontrol').hide();
    $('li.taskrow').mouseover(function(){
            $('li.taskrow').children().children().children().children().filter('.taskcontrols').show()
            
        });
    $('li.taskrow').mouseout(function(){
            $('li.taskrow').children().children().children().children().filter('.taskcontrols').hide()
            
        });
 });

 /*Handle the todo page accordian, and contexual menu.*/
 $(document).ready(function(){
    var handle_accordion = function(){
        $('.accordionitem').hide()
        $('#accordion a').addClass('collapsed')
        $(this).show()
        $(this).prev().addClass('uncollapsed')
        }
    var handle_acc_click = function(){
        $('#accordion a').removeClass('collapsed')
        $('#accordion a').removeClass('uncollapsed')
        $('#accordion .accordionitem').hide()
        $('#accordion a').addClass('collapsed')
        $(this).addClass('uncollapsed')
        $(this).next().show()
        }
    $('#accordion .accordionitem:first').each(handle_accordion)
    $('#accordion a').click(handle_acc_click);
    })
    /* Handle the showing of the per list forms.*/    
  $(document).ready(function(){
    var hidelistcontrols = function(){
        $(this).children().filter('.listcontrols').hide()
        }
    var showlistcontrols = function(){
        $(this).children().filter('.listcontrols').show()
        console.log(11)
        }
    $('.listcontrols').hide();
    $('#accordion .accordionitem,#accordion a').mouseover(showlistcontrols)
    $('#accordion .accordionitem').focus(showlistcontrols)
    $('#accordion .accordionitem').mouseout(hidelistcontrols)
    $('#accordion .accordionitem').blur(hidelistcontrols)
    });

 
