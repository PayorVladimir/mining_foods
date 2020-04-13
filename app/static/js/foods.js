$(function() {
    $('#groups-combo').combobox('reload', '/mining_foods/api/v1/groups_all');
});



              $('#dg').datagrid('enableFilter');

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
          dgterminals.datagrid('enableFilter');


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
