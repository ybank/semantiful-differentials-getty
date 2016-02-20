/**
 * the javascript file to import for semantiful differential html page
 */

function str2html(str) {
	console.log(str);
	return str.replace("<", "&lt;", "g").replace(">", "&gt;", "g").replace(/(?:\r\n|\r|\n)/g, '<br />');
}

function methodInvsCompare(theMtd, prev, post) {
//	compareInvs = $("div#" + theMtd)[0]
//	console.log(compareInvs);
	preInvs = $("invariants#" + theMtd).data(prev);
	console.log(preInvs);
	postInvs = $("invariants#" + theMtd).data(post);
	console.log(postInvs);
//	htmlContent = compareInvs + "<br>" + str2html(preInvs) + "<br>" + str2html(postInvs);
	htmlContent = str2html(preInvs) + "<br>" + str2html(postInvs);
	return htmlContent;
}

function installInvTips(newl2m, oldl2m) {
	postHash = newl2m[0];
	prevHash = oldl2m[0];
	
	// add invs for newl2m
	// consider added lines
	for (i = 1; i < newl2m.length; i += 3) {
		theFile = newl2m[i];
		theLine = newl2m[i+1];
		theMethod = newl2m[i+2];
		the_rows = $("tr.diffadded." + theFile)
		for (j = 0; j < the_rows.length; j ++) {			
			if (the_rows[j].childNodes[1].innerText == theLine) {
				the_rows.eq(j).simpletip({
					fixed: true, position: 'bottom',
					onBeforeShow: function() {
						this.update(methodInvsCompare(theMethod, prevHash, postHash));
					},
					onHide: function() {
						this.update("");
					},
					showTime: 200, hideTime: 0, hideEffect: 'none'
				});
			}
		}
	}
	//consider changed lines
	for (i = 1; i < newl2m.length; i += 3) {
		theFile = newl2m[i];
		theLine = newl2m[i+1];
		theMethod = newl2m[i+2];
		the_rows = $("tr.diffchanged." + theFile)
		for (j = 0; j < the_rows.length; j ++) {			
			if (the_rows[j].childNodes[2].innerText == theLine) {
				the_rows.eq(j).simpletip({
					fixed: true, position: 'bottom',
					onBeforeShow: function() {
						this.update(methodInvsCompare(theMethod, prevHash, postHash));
					},
					onHide: function() {
						this.update("");
					},
					showTime: 200, hideTime: 0, hideEffect: 'none'
				});
			}
		}
	}
	
	// add invs for oldl2m
	// consider delted lines
	for (i = 1; i < oldl2m.length; i += 3) {
		theFile = oldl2m[i];
		theLine = oldl2m[i+1];
		theMethod = oldl2m[i+2];
		the_rows = $("tr.diffdeleted." + theFile)
		for (j = 0; j < the_rows.length; j ++) {			
			if (the_rows[j].childNodes[0].innerText == theLine) {
				the_rows.eq(j).simpletip({
					fixed: true, position: 'bottom',
					onBeforeShow: function() {
						this.update(methodInvsCompare(theMethod, prevHash, postHash));
					},
					onHide: function() {
						this.update("");
					},
					showTime: 200, hideTime: 0, hideEffect: 'none'
				});
			}
		}
	}
}
