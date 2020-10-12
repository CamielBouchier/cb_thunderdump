//
// $BeginLicense$
//
// (C) 2020 by Camiel Bouchier (camiel@bouchier.be)
//
// This file is part of cb_thunderdump.
// All rights reserved.
//
// $EndLicense$
//

console.log("cb_thunderdump:cb_script started")

//
// Start our accompanying python script.
// See : https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging
//

var port = browser.runtime.connectNative("cb_thunderdump")

//
// Herein we will save our links.
//

var link_list = []

//
// Construct the links from the message list that the query generates.
// Separated out for use by messages.query and messages.continueList.
// Heavily async, be careful to have collected all before 'going further'.
//

async function handle_ml(ml) {
    // https://stackoverflow.com/questions/37576685/using-async-await-with-a-foreach-loop
    for (const the_message of ml.messages) {
        try {
            let full = await messenger.messages.getFull(the_message.id)
            let headers = full.headers
            let date = new Date(headers.date[0])
            let author = headers.from[0]
            let msg_id = headers['message-id'][0]
            let cb_link = btoa(date.toJSON() + ";" + author)
            link_list.push(cb_link + ";" + msg_id)
        } catch (e) {
            continue
        }
    }
}

//
// Start the query to all messages and handle them.
// Inform user about progress along the way.
// Heavily async, be careful to have collected all before 'going further'.
//

window.addEventListener('DOMContentLoaded', async (event) => {
    let div = document.getElementById('progress')
    div.innerHTML = "Initializing the dump process ..."
    let ml = await messenger.messages.query({})
    await handle_ml(ml)
    while (ml.id) {
        div.innerHTML = "Collected " + link_list.length + " tuples ..."
        ml = await messenger.messages.continueList(ml.id)
        await handle_ml(ml)
    }
    div.innerHTML = "Collected " + link_list.length + " tuples ..."
    div.innerHTML += "<br>Dumping " + link_list.length + " tuples ..."
    port.postMessage({'link_list': link_list})
})

//
// Await the reporting back from our accomanying script.
//

port.onMessage.addListener((response) => {
    let div = document.getElementById('progress')
    let nr_confirmed = response.cb_confirm
    div.innerHTML += "<br>Database confirmed " + nr_confirmed + " tuples out of " + link_list.length
    if (nr_confirmed == link_list.length) {
        div.innerHTML += "<br>Done ..."
    } else {
        div.innerHTML += "<br>Done with errors ..."
    }
    div.innerHTML += "<br>You can find the database at <i>" + response.db_name + "</i>" 

    // Let's help garbage collector a bit.
    link_list = []
})

//
// vim: syntax=javascript ts=4 sw=4 sts=4 sr et columns=100
//
