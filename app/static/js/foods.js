$(function() {
    $('#groups-combo').combobox('reload', '/mining_foods/api/v1/groups_all/');
});





            //terminals logs
          var dgterminals = $('#dg-terminals').datagrid({
                view: detailview,
                detailFormatter:function(index,row){
                    return '<div style="padding:2px;position:relative;"><table class="ddv"></table></div>';
                },
                onExpandRow: function(index,row){
                    var ddv = $(this).datagrid('getRowDetail',index).find('table.ddv');
                    ddv.datagrid({
                        url:'mining_foods/api/v1/logs?terminal_id='+row.terminal_id,
                        fitColumns:true,
                        singleSelect:true,
                        rownumbers:true,
                        remoteFilter: true,
                        loadMsg:'',
                        height:'auto',
                        columns:[[
                            {field:'log_id',title:'ID',width:50},
                            {field:'client_id',title:'ID клиента',width:100,},
                            {field:'client_name',title:'Имя клиента',width:100,},
                             {field:'client_card',title:'ID пропуска клиента',width:100,},
                             {field:'client_group_name',title:'Группа клиента',width:100,},
                            {field:'time_stamp',title:'Дата/время',width:100,}
                        ]],
                        onResize:function(){
                            $('#dg-terminals').datagrid('fixDetailRowHeight',index);
                        },
                        onLoadSuccess:function(){
                            setTimeout(function(){
                                $('#dg-terminals').datagrid('fixDetailRowHeight',index);
                            },0);
                        }
                    });
                    $('#dg-terminals').datagrid('fixDetailRowHeight',index);
                }
            });



var url;
var type;

function clientLogs(){
    var row = $('#dg').datagrid('getSelected');
     $('#client-logs').dialog('open').dialog('center').dialog('setTitle', 'Статистика: '+row.client_name);
        $('#logs').datagrid({url:'mining_foods/api/v1/logs?client_id='+row.client_id});
        $('#logs').datagrid('reload');
}

function clientSearch(){
    $('#dg').datagrid('load', {
        query: $('#client_search').val()
    });
}





function newUser() {
    $('#dlg').dialog('open').dialog('center').dialog('setTitle', 'Новый клиент');
    $('#fm').form('clear');
     $('#groups-combo').combobox('reload', '/mining_foods/api/v1/groups_all');
    url = '/mining_foods/api/v1/client';
    type = 'POST';
}

function editUser() {
    var row = $('#dg').datagrid('getSelected');
     $('#groups-combo').combobox('reload', '/mining_foods/api/v1/groups_all');
    if (row) {
        $('#dlg').dialog('open').dialog('center').dialog('setTitle', 'Редактировать профиль клиента');
        $('#fm').form('load', row);
        url = '/mining_foods/api/v1/client/' + row.client_id;
        type = 'PUT';

    }
}

function blockUser() {
    var row = $('#dg').datagrid('getSelected');
    var url = "/mining_foods/api/v1/block_client";
    if (row) {
        $.messager.confirm('Заблокировать клиента', 'Вы уверены, что хотите заблокировать этого клиента?', function (r) {
            if (r) {

                var data = {client_id: row.client_id}

                $.ajax({

                    url: url,
                    dataType: 'json',
                    type: 'PUT',
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify(data),
                    success: function (result) {

                         $('#dg').datagrid('reload');
                        $.messager.show({
                            title: 'Успешно',
                            msg:  result.message
                        });
                           // reload the user data
                    },
                    error: function (xhr) {
                        $.messager.show({
                            title: 'Ошибка',
                            msg: JSON.parse(xhr.responseText)['message']
                        });
                    }


                });
            }
        });
    }
}

function activateUser() {

     var row = $('#dg').datagrid('getSelected');
    var url = "/mining_foods/api/v1/activate_client";
    if (row) {
        $.messager.confirm('Заблокировать клиента', 'Вы уверены, что хотите разблокировать этого клиента?', function (r) {
            if (r) {

                var data = {client_id: row.client_id}

                $.ajax({

                    url: url,
                    dataType: 'json',
                    type: 'PUT',
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify(data),
                    success: function (result) {

                         $('#dg').datagrid('reload');
                        $.messager.show({
                            title: 'Успешно',
                            msg:  result.message
                        });
                           // reload the user data
                    },
                    error: function (xhr) {
                        $.messager.show({
                            title: 'Ошибка',
                            msg: JSON.parse(xhr.responseText)['message']
                        });
                    }


                });
            }
        });
    }
}

function saveUser() {


    var client_name = document.forms["fm"]["client_name"].value;
    var card_id = document.forms["fm"]["card_id"].value;
    var quota = document.forms["fm"]["quota"].value;
    var group = document.forms["fm"]["group"].value;
    var data = {card_id: card_id, client_name: client_name, quota: quota, group: group};

    $.ajax({

        url: url,
        dataType: 'json',
        type: type,
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(data),

        success: function (result) {



            $('#dlg').dialog('close');        // close the dialog
            $('#dg').datagrid('reload');    // reload the user data
        },
        error: function (xhr) {
            $.messager.show({
                title: 'Ошибка',
                msg: JSON.parse(xhr.responseText)['message']
            });
        }


    });

}

function destroyUser() {
    var row = $('#dg').datagrid('getSelected');
    var url = "/mining_foods/api/v1/client";
    if (row) {
        $.messager.confirm('Удалить клиента', 'Вы уверены, что хотите удалить профиль этого клиента?', function (r) {
            if (r) {

                var data = {client_id: row.client_id}

                $.ajax({

                    url: url,
                    dataType: 'json',
                    type: 'DELETE',
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify(data),
                    success: function (result) {

                         $('#dg').datagrid('reload');
                        $.messager.show({
                            title: 'Успешно',
                            msg:  result.message
                        });
                           // reload the user data
                    },
                    error: function (xhr) {
                        $.messager.show({
                            title: 'Ошибка',
                            msg: JSON.parse(xhr.responseText)['message']
                        });
                    }


                });
            }
        });
    }
}

function newAccount() {
    $('#dlg-users').dialog('open').dialog('center').dialog('setTitle', 'Новый пользователь');
    $('#fm-users').form('clear');
    url = '/mining_foods/api/v1/new_user';
    type = 'POST';
}

function blockAccount() {
     var row = $('#dg-users').datagrid('getSelected');
    var url = "/mining_foods/api/v1/block_user";
    if (row) {
        $.messager.confirm('Заблокировать пользователя', 'Вы уверены, что хотите заблокировать этого пользователя?', function (r) {
            if (r) {

                var data = {user_id: row.user_id}

                $.ajax({

                    url: url,
                    dataType: 'json',
                    type: 'PUT',
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify(data),
                    success: function (result) {

                         $('#dg-users').datagrid('reload');
                        $.messager.show({
                            title: 'Успешно',
                            msg:  result.message
                        });
                           // reload the user data
                    },
                    error: function (xhr) {
                        $.messager.show({
                            title: 'Ошибка',
                            msg: JSON.parse(xhr.responseText)['message']
                        });
                    }


                });
            }
        });
    }
}

function deleteAccount(){
    var row = $('#dg-users').datagrid('getSelected');
    var url = "/mining_foods/api/v1/users";
    if (row) {
        $.messager.confirm('Удалить клиента', 'Вы уверены, что хотите удалить профиль этого пользователя?', function (r) {
            if (r) {

                var data = {user_id: row.user_id}

                $.ajax({

                    url: url,
                    dataType: 'json',
                    type: 'DELETE',
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify(data),
                    success: function (result) {

                         $('#dg-users').datagrid('reload');
                        $.messager.show({
                            title: 'Успешно',
                            msg:  result.message
                        });
                           // reload the user data
                    },
                    error: function (xhr) {
                        $.messager.show({
                            title: 'Ошибка',
                            msg: JSON.parse(xhr.responseText)['message']
                        });
                    }


                });
            }
        });
    }
}

function editAccount() {
    var row = $('#dg-users').datagrid('getSelected');
    if (row) {
        $('#dlg-users').dialog('open').dialog('center').dialog('setTitle', 'Редактировать профиль клиента');
        $('#fm-users').form('load', row);
        url = '/mining_foods/api/v1/users/' + row.user_id;
        type = 'PUT';

    }

}

function saveAccount() {
    var login = document.forms["fm-users"]["user_login"].value;
    var username = document.forms["fm-users"]["user_name"].value;
    var password = document.forms["fm-users"]["user_password"].value;
    var data = {login: login, username: username, password: password};

    $.ajax({

        url: url,
        dataType: 'json',
        type: type,
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(data),

        success: function (result) {

            $('#dlg-users').dialog('close');        // close the dialog
            $('#dg-users').datagrid('reload');    // reload the user data
        },
        error: function (xhr) {
            $.messager.show({
                title: 'Ошибка',
                msg: JSON.parse(xhr.responseText)['message']
            });
        }


    });

}

function activateAccount() {
     var row = $('#dg-users').datagrid('getSelected');
    var url = "/mining_foods/api/v1/activate_user";
    if (row) {
        $.messager.confirm('Разблокировать пользователя', 'Вы уверены, что хотите разблокировать этого пользователя?', function (r) {
            if (r) {

                var data = {user_id: row.user_id}

                $.ajax({

                    url: url,
                    dataType: 'json',
                    type: 'PUT',
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify(data),
                    success: function (result) {

                         $('#dg-users').datagrid('reload');
                        $.messager.show({
                            title: 'Успешно',
                            msg:  result.message
                        });
                           // reload the user data
                    },
                    error: function (xhr) {
                        $.messager.show({
                            title: 'Ошибка',
                            msg: JSON.parse(xhr.responseText)['message']
                        });
                    }


                });
            }
        });
    }
}

function blockTerminal() {
    var row = $('#dg-terminals').datagrid('getSelected');
    var url = "/mining_foods/api/v1/block_terminal";
    if (row) {
        $.messager.confirm('Заблокировать терминал', 'Вы уверены, что хотите заблокировать этот терминал?', function (r) {
            if (r) {

                var data = {terminal_id: row.terminal_id}

                $.ajax({

                    url: url,
                    dataType: 'json',
                    type: 'PUT',
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify(data),
                    success: function (result) {

                         $('#dg-terminals').datagrid('reload');
                        $.messager.show({
                            title: 'Успешно',
                            msg:  result.message
                        });
                           // reload the user data
                    },
                    error: function (xhr) {
                        $.messager.show({
                            title: 'Ошибка',
                            msg: JSON.parse(xhr.responseText)['message']
                        });
                    }


                });
            }
        });
    }
}

function activateTerminal() {
    var row = $('#dg-terminals').datagrid('getSelected');
    var url = "/mining_foods/api/v1/activate_terminal";
    if (row) {
        $.messager.confirm('Активировать терминал', 'Вы уверены, что хотите активировать этот терминал?', function (r) {
            if (r) {

                var data = {terminal_id: row.terminal_id}

                $.ajax({

                    url: url,
                    dataType: 'json',
                    type: 'PUT',
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify(data),
                    success: function (result) {

                         $('#dg-terminals').datagrid('reload');
                        $.messager.show({
                            title: 'Успешно',
                            msg:  result.message
                        });
                           // reload the user data
                    },
                    error: function (xhr) {
                        $.messager.show({
                            title: 'Ошибка',
                            msg: JSON.parse(xhr.responseText)['message']
                        });
                    }


                });
            }
        });
    }
}

function deleteTerminal() {
    var row = $('#dg-terminals').datagrid('getSelected');
    var url = "/mining_foods/api/v1/delete_terminal";
    if (row) {
        $.messager.confirm('Удалить терминал', 'Вы уверены, что хотите удалить этот терминал? Терминал будет заблокирован, а все записи о нем стерты из базы данных.', function (r) {
            if (r) {

                var data = {terminal_id: row.terminal_id}

                $.ajax({

                    url: url,
                    dataType: 'json',
                    type: 'DELETE',
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify(data),
                    success: function (result) {

                         $('#dg-terminals').datagrid('reload');
                        $.messager.show({
                            title: 'Успешно',
                            msg:  result.message
                        });
                           // reload the user data
                    },
                    error: function (xhr) {
                        $.messager.show({
                            title: 'Ошибка',
                            msg: JSON.parse(xhr.responseText)['message']
                        });
                    }


                });
            }
        });
    }
}

function editTerminal() {

      var row = $('#dg-terminals').datagrid('getSelected');
    if (row) {
        $('#dlg-terminals').dialog('open').dialog('center').dialog('setTitle', 'Редактировать запись о терминале');
        $('#fm-terminals').form('load', row);

        url = '/mining_foods/api/v1/terminals/'+ row.terminal_id;

    }

}

function saveTerminal() {
      var description = document.forms["fm-terminals"]["terminal_description"].value;

        var data = { terminal_description: description};


        $.ajax({

            url: url,
            dataType: 'json',
            type: "PUT",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify(data),

            success: function (result) {


                $('#dlg-terminals').dialog('close');        // close the dialog
                $('#dg-terminals').datagrid('reload');    // reload terminals table
            },
            error: function (xhr) {
                $.messager.show({
                    title: 'Ошибка',
                    msg: JSON.parse(xhr.responseText)['message']
                });
            }


        });
}


function newGroup() {
    $('#dlg-groups').dialog('open').dialog('center').dialog('setTitle', 'Новая группа клиентов');
    $('#fm-groups').form('clear');
    url = '/mining_foods/api/v1/new_group';
    type = 'POST';
}

function blockGroup() {
     var row = $('#dg-groups').datagrid('getSelected');
    var url = "/mining_foods/api/v1/block_group";
    if (row) {
        $.messager.confirm('Заблокировать группу', 'Вы уверены, что хотите заблокировать эту  группу клиентов?', function (r) {
            if (r) {

                var data = {group_id: row.group_id}

                $.ajax({

                    url: url,
                    dataType: 'json',
                    type: 'PUT',
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify(data),
                    success: function (result) {

                         $('#dg-groups').datagrid('reload');
                        $.messager.show({
                            title: 'Успешно',
                            msg:  result.message
                        });
                           // reload the user data
                    },
                    error: function (xhr) {
                        $.messager.show({
                            title: 'Ошибка',
                            msg: JSON.parse(xhr.responseText)['message']
                        });
                    }


                });
            }
        });
    }
}


function activateGroup() {
     var row = $('#dg-groups').datagrid('getSelected');
    var url = "/mining_foods/api/v1/activate_group";
    if (row) {
        $.messager.confirm('Разблокировать группу', 'Вы уверены, что хотите разблокировать эту  группу клиентов?', function (r) {
            if (r) {

                var data = {group_id: row.group_id}

                $.ajax({

                    url: url,
                    dataType: 'json',
                    type: 'PUT',
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify(data),
                    success: function (result) {

                         $('#dg-groups').datagrid('reload');
                        $.messager.show({
                            title: 'Успешно',
                            msg:  result.message
                        });
                           // reload the user data
                    },
                    error: function (xhr) {
                        $.messager.show({
                            title: 'Ошибка',
                            msg: JSON.parse(xhr.responseText)['message']
                        });
                    }


                });
            }
        });
    }
}

function deleteGroup(){
    var row = $('#dg-groups').datagrid('getSelected');
    var url = "/mining_foods/api/v1/delete_group";
    if (row) {
        $.messager.confirm('Удалить группу', 'Вы уверены, что хотите удалить профиль этой группы клиентов?', function (r) {
            if (r) {

                var data = {group_id: row.group_id}

                $.ajax({

                    url: url,
                    dataType: 'json',
                    type: 'DELETE',
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify(data),
                    success: function (result) {

                         $('#dg-groups').datagrid('reload');
                        $.messager.show({
                            title: 'Успешно',
                            msg:  result.message
                        });
                           // reload the user data
                    },
                    error: function (xhr) {
                        $.messager.show({
                            title: 'Ошибка',
                            msg: JSON.parse(xhr.responseText)['message']
                        });
                    }


                });
            }
        });
    }
}

function editGroup() {
    var row = $('#dg-groups').datagrid('getSelected');
    if (row) {
        $('#dlg-groups').dialog('open').dialog('center').dialog('setTitle', 'Редактировать профиль группы');
        $('#fm-groups').form('load', row);
        url = '/mining_foods/api/v1/groups/' + row.group_id;
        type = 'PUT';

    }

}

function saveGroup() {
    var title = document.forms["fm-groups"]["group_title"].value;
    // var valid_thru = document.forms["fm-groups"]["group_valid_thru"].value;
    var data = {group_title: title};

    $.ajax({

        url: url,
        dataType: 'json',
        type: type,
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(data),

        success: function (result) {

            $('#dlg-groups').dialog('close');        // close the dialog
            $('#dg-groups').datagrid('reload');    // reload the user data
        },
        error: function (xhr) {
            $.messager.show({
                title: 'Ошибка',
                msg: JSON.parse(xhr.responseText)['message']
            });
        }


    });

}

function loadExcel(id) {

        let url = '/mining_foods/stats/terminal/' + id;

         return new Promise(function(resolve, reject) {
    // Get file name from url.
    let xhr = new XMLHttpRequest();
    xhr.responseType = 'blob';
    xhr.onload = function() {
      resolve(xhr);
    };
    xhr.onerror = reject;
    xhr.open('GET', url);
    xhr.send();
  }).then(function(xhr) {
    var filename = "Выгрузка_терминал_"+id;
    var a = document.createElement('a');
    a.href = window.URL.createObjectURL(xhr.response); // xhr.response is a blob
    a.download = filename; // Set the file name.
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    return xhr;
  });
}



var getDates = function(startDate, endDate) {

  var dates = [],
      currentDate = startDate,
      addDays = function(days) {
        var date = new Date(this.valueOf());
        date.setDate(date.getDate() + days);
        return date;
      };
  while (currentDate <= endDate) {
    dates.push(currentDate.getDate());
    currentDate = addDays.call(currentDate, 1);
  }
  return dates;
};

var lastWeek = new Date();
var today = new Date()
lastWeek.setDate(lastWeek.getDate() - 6);
var dates = getDates(lastWeek,today);



function logsSearch(){
    $('#dg-logs').datagrid('load', {
        query: $('#logs_search').val()
    });
}





$( "#tokensList" ).ready(function() {
    updateTokensList();
});


function copyToClipbooard(id){

  var copyText = document.getElementById(id);
  copyText.select();
  copyText.setSelectionRange(0, 99999)
  document.execCommand("copy");

}

var tokens = []
var selected_token;
function updateTokensList() {
    $.get("https://digital.spmi.ru/mining_foods/api/v1/settings", function (data, status) {
        tokens = [];
         tokens = data.settings;
            $("#tokensList").empty()

       for (let i = 0; i < tokens.length; i++) {
             let token_label = tokens[i]["label"];
            $("#tokensList").append('<li> <b class="w3-text-black " style="width:35px;font-size: 12pt">' + tokens[i]["label"]+'</b>  <textarea readonly cols="64" rows="1" style="resize:none" id="token-'+i+'">'+ tokens[i]["value"]+'</textarea> <span onclick=copyToClipbooard("token-'+i+'") <i class = "fas fa-copy w3-text-teal w3-large"></i></span>     <span onclick=tokenToDelete("'+i+'") <i class = "fas fa-trash w3-text-red w3-large"></i></span>   </li> ');
        }
    });
}



function tokenToDelete(value) {
document.getElementById('deleteTokenModal').style.display='block';
selected_token = tokens[value]["value"];
document.getElementById("deleteTokenMsg").innerHTML = "Вы действительно хотите удалить токен "+tokens[value]["label"] +"? Его удаление может привести к отключению клиентских приложений.";

}

function deleteToken() {

    $.ajax({
  type: "DELETE",
  url: "https://digital.spmi.ru/mining_foods/api/v1/settings/"+selected_token,
         success: function() { updateTokensList();
  document.getElementById('deleteTokenModal').style.display='none';}
});

updateTokensList();
}

function addToken() {
    var label_v = $('#tokenName').val();
    $.ajax({
  type: "POST",
  url: "https://digital.spmi.ru/mining_foods/api/v1/settings",
  data: JSON.stringify({label: label_v}),
  contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function() { updateTokensList(); }
});
document.getElementById('addTokenModal').style.display='none';
updateTokensList();
}



function updatePin() {
    var pin_v = $('#pinInput').val();
    $.ajax({
  type: "PATCH",
  url: "https://digital.spmi.ru/mining_foods/api/v1/settings/update_pin",
  data: JSON.stringify({pin: pin_v}),
  contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function() { document.getElementById('editPin').style.display='none'; }
});

document.getElementById('editPin').style.display='none';
updateTokensList();
}


$( "#datepicker" ).datepicker();
$( "#datepicker" ).datepicker("setDate", today);

var stats = document.getElementById('barStatsChart').getContext('2d');

 $.get("https://digital.spmi.ru/mining_foods/api/v1/stats", function (data) {
        var myChart = new Chart(stats, {
    type: 'bar',
    data: {

        labels: dates,
        datasets: [{

            data: data["rows"],


            backgroundColor: function(context) {
                        var index = context.dataIndex;
                            var value = context.dataset.data[index];
                                return value > 1000 ? 'red' :  // draw negative values in red
                              value > 500 ? 'orange' :    // else, alternate values in blue and green
                                         'green';
},
            borderColor: function(context) {
                        var index = context.dataIndex;
                            var value = context.dataset.data[index];
                                return value > 1000 ? 'red' :  // draw negative values in red
                              value > 500 ? 'orange' :    // else, alternate values in blue and green
                                         'green';
},
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true
                }
            }]
        },
        title: {
            display: true,
            text: 'Количество обращений к системе за день'
        },
         legend: {
             display: false,
         }
    }
});



    });


