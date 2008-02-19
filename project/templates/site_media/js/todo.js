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