/**
 * the javascript file to import for semantiful differential html page
 */

//deprecated
function invstr2html(str, pos) {
	style = "width:48%;max-height:400px;overflow:auto;padding:5px 5px 5px 5px;";
	if (pos == "left")
		style += "display:inline-block;position:relative;" + 
			"border:2px dotted #A8BBA8;background:#5A5F5A;color:white;";
	else if (pos == "right")
		style += "display:inline-block;position:absolute;right:15px;" + 
			"border:2px dotted #A8BBA8;background:#5A5F5A;color:white;";
	else
		console.error('incorrect pos arg passed to invstr2html(): it should be either "left" or "right"');
	start = "<p style='" + style + "'>\n";
	body = str.replace("&", "&amp;", "g").replace("<", "&lt;", "g").replace(">", "&gt;", "g");
	body = withLineNumbers(body, 1);
	body = body.replace(/(?:\r\n|\r|\n)/g, '<br />');
	end = "\n</p>";
	return start + body + end;
}

//deprecated
function methodInvsCompare(theMtd, prev, post) {
	compareInvs = $("div#vsinvs-" + theMtd)[0].outerHTML;
	preInvs = $("invariants#" + theMtd).data(prev);
	postInvs = $("invariants#" + theMtd).data(post);
	htmlContent = compareInvs + invstr2html(preInvs, "left") + invstr2html(postInvs, "right");
	return "<body>" + htmlContent + "</body>";
}

// style for source code if needed
// style = "max-width:400px;max-height:400px;overflow:auto;padding:5px 5px 5px 5px";

//deprecated
function withLineNumbers(content, start) {
	var content_with_ln = "";
	var lines = content.split(/(?:\r\n|\r|\n)/);
	for (j = 0, i = start; j < lines.length; j ++, i ++) {
		ln = "" + i;
		if (ln.length < 3)
			ln = "&nbsp;".repeat(3 - ln.length) + ln;
		content_with_ln += ("<span>" + ln +"&nbsp;|&nbsp;&nbsp;&nbsp;</span>" + lines[j]) + "\n";
	}
	return content_with_ln;
}

//deprecated
function installInvTips_old(newl2m, oldl2m) {
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

function methodInvsComparePage(theMtd, prev, post) {
	compareInvs = $("div#vsinvs-" + theMtd)[0].outerHTML;
//	compareInvs = $("div#vsinvs-org_joda_time_tz_ZoneInfoCompiler_main")[0].outerHTML;
	left = 
		"width:48%;height:400px;background-color: #5A5F5A;" + 
		"display:inline-block;position:relative;border:2px dotted #A8BBA8;";
	preInvs = 
		"<iframe src='./_getty_inv__" + theMtd + "__" + prev + "_.inv.html' " +
				"class='invtip' style='" + left + "'></iframe>";
	right = 
		"width:48%;height:400px;background-color: #5A5F5A;" + 
		"display:inline-block;position:absolute;right:15px;border:2px dotted #A8BBA8;";
	postInvs = 
		"<iframe src='./_getty_inv__" + theMtd + "__" + post + "_.inv.html' " +
				"class='invtip' style='" + right + "'></iframe>";
	htmlContent = compareInvs + "<br>" + preInvs + postInvs;
	return "<body>" + htmlContent + "</body>";
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
						this.update(methodInvsComparePage(theMethod, prevHash, postHash));
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
						this.update(methodInvsComparePage(theMethod, prevHash, postHash));
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
						this.update(methodInvsComparePage(theMethod, prevHash, postHash));
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

function installAdvisorTips(adviceFile) {
	var style = "width:800px;height:400px;";
	$("#getty-advice-title").eq(0).simpletip({
		fixed: true, position: ["100px", "15px"],
		content: "<iframe src='./" + adviceFile + "' class='advtip' style='" + style + "'></iframe>",
		showTime: 200, hideTime: 0, hideEffect: 'none'
	})
}

