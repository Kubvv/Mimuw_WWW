
function changeVisibility(index) {
    var x = document.getElementById("section" + index);
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}

function showFile(pk) {
    $.ajax({
        url: '/ajax/show_file/',
        data: {
            'pk': pk
        },
        dataType: 'json',
        success: function (data) {
            document.getElementById("main-section").innerHTML = data.content;
            editElementsSection(data.frama);
        }
    });
}

function compile() {
    $.ajax({
        url: '/ajax/compile/',
        dataType: 'json',
        success: function (data) {
            var frama = data.frama;
            if (frama == "") {
                return;
            }
            editElementsSection(frama);
        }
    });
}

function deleteView() {
    $.ajax({
        url: '/ajax/delete/',
        dataType: 'json',
        success: function (data) {
            var dirs = data.all_dire;
            var files = data.all_files;
            document.getElementById('elements-section').innerHTML = "";
            deletion = document.getElementById('main-section');
            deletion.innerHTML = "";
            for (var i = 0; i < dirs.length; i++) {
                deletion.innerHTML += '<div class="deletion"><p class="deletion-left">' + dirs[i][0] + '</p>'
                + `<button class="deletion-right" onclick="deleteDirectory(` + dirs[i][1] + `)"><span class="hover-text">Delete</span></button></div>`;
                for (var j = 0; j < files[i].length; j++) {
                    if (files[i][j][1]) {
                        deletion.innerHTML += '<div class="deletion"><p class="deletion-left-file">' + files[i][j][0] + '</p>'
                        + `<button class="deletion-right" onclick="deleteFile(` + files[i][j][2] + `)"><span class="hover-text">Delete</span></button></div>`;
                    }
                }
            }
        }
    });
}

function deleteFile(pk) {
    $.ajax({
        url: '/ajax/delete_file/',
        data: {
            'pk': pk
        },
        dataType: 'json',
        success: function (data) {
            document.getElementById("FileNo" + pk).style.display = "none";
            deleteView();
        }
    })
}

function deleteDirectory(pk) {
    $.ajax({
        url: '/ajax/delete_dir/',
        data: {
            'pk': pk
        },
        dataType: 'json',
        success: function (data) {
            document.getElementById("DirNo" + pk).style.display = "none";
            dirpk = data.dirpk;
            filepk = data.filepk;
            for (var i = 0; i < dirpk.length; i++) {
                document.getElementById("DirNo" + dirpk[i]).style.display = "none";
            }
            for (var i = 0; i < filepk.length; i++) {
                document.getElementById("FileNo" + filepk[i]).style.display = "none";
            }
            deleteView();
        }
    })
}

function editElementsSection(frama) {
    var elements = document.getElementById('elements-section');
    elements.innerHTML = "";
    for (var i = 0; i < frama.length; i++) {
        elements.innerHTML += '<div><p class="norm-text">------------------------------------------------------------</p>'
        + '<button class="small" onclick="changeVisibility(' + i + ')">+</button></div>';
        if (frama[i][4]) {
            elements.innerHTML += '<div class="frama' + frama[i][0] + '">'
            + '<p class="norm-text">' + frama[i][3] + ',' + frama[i][4] + '</p></div>';
        }
        elements.innerHTML += '<div id="section' + i + '" class="frama' + frama[i][0] + '">'
        + '<p class="norm-text"><abbr title="' + frama[i][1] + frama[i][3] + '">' + frama[i][2] + '</abbr></p></div>';
    }
}

function changeTheme() {
    var body = document.getElementById('body');
    var theme;
    if (body.classList.contains('normal-color')) {
        body.classList.add('alt-color');
        body.classList.remove('normal-color');
        theme = "alt-color";
    }
    else {
        body.classList.add('normal-color');
        body.classList.remove('alt-color');
        theme = "normal-color";
    }

    $.ajax({
        url: '/ajax/change_theme/',
        data: {
            'theme': theme
        },
        dataType: 'json',
        success: function (data) {}
    })
}