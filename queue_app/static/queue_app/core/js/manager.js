(function($){
	
	$.fn.list_booth = function(url){
		var $this = $(this);
		$.ajax({
    		url : url,
    		type : "GET",
    		dataType: 'html',
    	})
    	.fail(function(xhr){
    		var error_message = "AJAX Err:\n";
    		error_message += "["+xhr.status.toString()+"] : ";
    		error_message += xhr.statusText;
    		window.alert(error_message);
    	})
    	.done(function(data){
    		$this.append(data);
    	});
	};
	$.fn.booking_form_popup = function(){
		$(this).on('click',function(event){
			event.preventDefault();
			var popup_window = window.open($(this).attr('href'),"_blank","width=1000,height=1000'");
			
		});
	};
}(jQuery));