(function($){
	
	$.fn.list_booth = function(){
		var $this = $(this);
		url = $this.attr('booth_url');
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
	
	$.fn.get_initial_queue_list = function(){
		$.each(this,function(idx,dom_obj){
			queue_url = $(dom_obj).attr('queues_url');
			$.ajax({
				url:queue_url,
				type:'GET',
				dataType:'html',
				contentType: 'application/x-www-form-urlencoded',				
			})
			.fail(function(xhr){
				window.alert(xhr.status.toString());
			})
			.done(function(response){
				$(dom_obj).append(response);
			});
		});
	};
}(jQuery));