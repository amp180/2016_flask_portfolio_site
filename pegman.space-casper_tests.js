
var xpath = require('casper').selectXPath
 
casper.test.begin('Home page loads successfully.', 3,  function(){
	casper.start('http://pegman.space/');
	
	casper.then(function() {
		casper.test.assertTitle("Home - Pegman.Space", "Title correct.")
		//check that message was included properly
		casper.test.assertExists( xpath('/html/body/div[@class="container body-content"]/figure'), "Content included." )
		//check footer is in correct place, won't be if I miss a closing tag
		casper.test.assertExists(xpath('/html/body/div/footer'), "Footer in correct place.") 
		}
	);
		
	casper.run(function(){ casper.test.done()});
});

casper.test.begin('CV loads successfully.', 2,  function(){
	casper.start('http://pegman.space/cv');
	
	casper.then(function() {
		casper.test.assertTitle("CV - Pegman.Space", "Title correct.")
		
		//check sections show up
		casper.test.assertElementCount('.panel-default', 7)
		}
	);
		
	casper.run(function(){ casper.test.done()});
});

casper.test.begin('IP checker works.', 3,  function(){
	casper.start('http://pegman.space/ip');
	
	casper.then(function() {
		casper.test.assertTitle("Home - Pegman.Space", "Title correct.")
		
		//The ip address checker uses flask's flash feature to include a message in the next page loaded
		//then redirects you to the home page. This test checks that the message actually gets included.
		
		var flashed_message_xpath = xpath('/html/body/div[@class="container body-content"]/ul/li/span')
		
		casper.test.assertExists(
			flashed_message_xpath,
			"A message was flashed." 
		)
		
		casper.test.assertMatch(
					casper.fetchText(flashed_message_xpath),
					/[0-9]{1,4}(.[0-9]{1,4}){3}/,
					"Flashed message roughly looks like an ip address."
					); 
		}
	);
		
	casper.run(function(){ casper.test.done()});
});
 
casper.test.begin('DCU lab checker works.', 11,  function(){
	casper.start('http://pegman.space/dcu_rooms');
	
	casper.then(function() {
		casper.test.assertTitle("DCU Lab Bookings - Pegman.Space", "Title correct.")
		
		//check all the rooms show up
		casper.test.assertElementCount('.room_status', 9)
		
		//Get the text from the room entries, 
		//needs casper.evaluate because the dom isn't directly accessible from this context.
		var rooms = casper.evaluate( function(){
			return __utils__.findAll('div.room_status')
				.map(function(room){return room.innerHTML})
		});
		
		//Check the room messages match up and the timetables successfully fetch
		rooms.forEach( function(room){
			casper.test.assertMatch(
				room, 
				/(L|C)(G|0|1|2)[0-9]{1,3}: ((Booked)|(Free)|(Closed))/,
				"Matches normal pattern: " + room.trim()
				)
		});
		
	});
		
	casper.run(function(){ casper.test.done()});
}); 
