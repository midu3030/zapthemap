function wordMap(){

	//find words in the document text
	if(this.body == null){
		return;
	}
	
	var words = this.body.match(/\w+/g);
	
	if (words == null){
		return;
	}
	
	
	for (var i = 0; i < words.length; i++){
		//emit every word, with count of one
		emit(words[i].toLowerCase(), {count: 1});
	
	}


}