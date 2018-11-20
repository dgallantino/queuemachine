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
	
	$.fn.as_booking_form_modal = function(){
		$(this).on('click',function(event){
			event.preventDefault();
			var popup_window = window.open($(this).attr('href'),"_blank","width=1000,height=1000'");
			
		});
	};
	
	//request the most updated queue list
	$.fn.as_queue_list = function(){
		$.each(this,function(idx,dom_obj){
			var queue_url = $(dom_obj).attr('queues_url');
			var loading_html =	'<tr><td class ="text-center" colspan="5">';
			loading_html += '<i class="fa fa-spinner fa-pulse fa-3x fa-fw"></i>';
			loading_html += '<span class="sr-only">Loading...</span>';
			loading_html += '</td></tr>';
			$(dom_obj).html(loading_html);
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
				$(dom_obj).html(response);
			});
		});
		return false;
	};
}(jQuery));