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

 
