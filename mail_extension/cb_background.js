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

console.log("cb_thunderdump:cb_background started")

messenger.browserAction.onClicked.addListener(async () => {
    browser.tabs.create({url: "cb_tab.html"})
})

// vim: syntax=javascript ts=4 sw=4 sts=4 sr et columns=100
