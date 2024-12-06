
$(function () {
});

function loadData(url, method, data) {
  $.ajax({
    url: url,
    type: method,
    data: data.length > 0 ? data : '',
    success: function (data) {
      $('.main-panel').html(data.html);
    },
    error: function (xhr, status, error) {
      alert('Error loading data: ' + error);
    }
  });
}

function errorMarker(element) {
  element.parent().find('.field-error').remove();
  if (element.val().length < 1) {
    var fieldError = $('<label class="text-danger field-error">This field is required</label>');
    fieldError.insertAfter(element);
  }
}

function saveNewRole() {
  if ($("#role-name").val().length < 1) {
    errorMarker($("#role-name"));
  } else {
    $.ajax({
      url: 'users/user-role-list/',
      type: 'POST',
      data: { "name": $("#role-name").val(), "desc": $("#role-description").val(), 'action': 'save' },
      success: function (data) {
        $("#new-role-modal-btn").click();
        setTimeout(() => {
          loadData('users/user-role-list/', 'GET', '');
        }, 500);
      },
      error: function (xhr, status, error) {
        alert('Error loading data: ' + error);
      }
    });
  }
}

function openNewRoleModal() {
  $('.field-error').remove();
  $("#role-name").val("");
  $("#role-description").val("");
}

function closeNewUserRoleModal() {
  $("#role-name").val("");
  $("#role-description").val("");
}

function openEditRoleModal(id) {
  $('.field-error').remove();
  $('#edit-user-role-dialog').modal('show');
  $.ajax({
    url: 'users/user-role-list/',
    type: 'GET',
    data: { 'id': id, 'action': 'edit' },
    success: function (data) {
      $('#edit-user-role-dialog').find('.modal-body').html(data.html);
    },
    error: function (xhr, status, error) {
      alert('Error loading data: ' + error);
    }
  });
}

function closeEditRoleModal() {
  $("#edit-role-name").val("");
  $("#edit-role-description").val("");
}

function saveEditRole() {
  if ($("#edit-role-name").val().length < 1) {
    errorMarker($("#edit-role-name"));
  } else {
    $.ajax({
      url: 'users/user-role-list/',
      type: 'POST',
      data: { "id": $("#edit-role-id").val(), "name": $("#edit-role-name").val(), "desc": $("#edit-role-description").val(), 'action': 'edit' },
      success: function (data) {
        $("#edit-user-role-dialog").modal('hide');
        setTimeout(() => {
          loadData('users/user-role-list/', 'GET', '');
        }, 500);
      },
      error: function (xhr, status, error) {
        alert('Error loading data: ' + error);
      }
    });
  }
}

function saveNewDeparment() {
  if ($("#department-name").val().length < 1) {
    errorMarker($("#department-name"));
  } else {
    $.ajax({
      url: 'users/department-list/',
      type: 'POST',
      data: { "name": $("#department-name").val(), "desc": $("#department-description").val() },
      success: function (data) {
        $("#new-department-modal-btn").click();
        setTimeout(() => {
          loadData('users/department-list/', 'GET', '');
        }, 500);
      },
      error: function (xhr, status, error) {
        alert('Error loading data: ' + error);
      }
    });
  }
}

function openNewDepartmentModal() {
  $('.field-error').remove();
  $("#department-name").val("");
  $("#department-description").val("");
}

function closeNewDepartmentModal() {
  $("#department-name").val("");
  $("#department-description").val("");
}

function openEditDepartmentModal(id) {
  $('.field-error').remove();
  $('#edit-department-dialog').modal('show');
  $.ajax({
    url: 'users/department-list/',
    type: 'GET',
    data: { 'id': id, 'action': 'edit' },
    success: function (data) {
      $('#edit-department-dialog').find('.modal-body').html(data.html);
    },
    error: function (xhr, status, error) {
      alert('Error loading data: ' + error);
    }
  });
}

function closeEditDepartmentModal() {
  $("#edit-department-name").val("");
  $("#edit-department-description").val("");
}

function saveEditDepartment() {
  if ($("#edit-department-name").val().length < 1) {
    errorMarker($("#edit-department-name"));
  } else {
    $.ajax({
      url: 'users/department-list/',
      type: 'POST',
      data: { "id": $("#edit-department-id").val(), "name": $("#edit-department-name").val(), "desc": $("#edit-department-description").val(), 'action': 'edit' },
      success: function (data) {
        $("#edit-department-dialog").modal('hide');
        setTimeout(() => {
          loadData('users/department-list/', 'GET', '');
        }, 500);
      },
      error: function (xhr, status, error) {
        alert('Error loading data: ' + error);
      }
    });
  }
}

function validateUser() {
  var isValid = true;
  $(".field-error").remove();

  if ($("#first-name").val().length < 1) {
    errorMarker($("#first-name"));
    isValid = false;
  }

  if ($("#last-name").val().length < 1) {
    errorMarker($("#last-name"));
    isValid = false;
  }

  if ($("#username").val().length < 1) {
    errorMarker($("#username"));
    isValid = false;
  }

  if ($("#department").val().length < 1) {
    errorMarker($("#department"));
    isValid = false;
  }

  if ($("#user-role").val().length < 1) {
    errorMarker($("#user-role"));
    isValid = false;
  }

  if ($("#email").val().length < 1) {
    errorMarker($("#email"));
    isValid = false;
  }

  if ($("#password").val().length < 1) {
    errorMarker($("#password"));
    isValid = false;
  }

  if ($("#retype-password").val().length < 1) {
    errorMarker($("#retype-password"));
    isValid = false;
  }

  if ($("#password").val().length > 0 && $("#retype-password").val().length > 0) {
    $("#retype-password").parent().find('.field-error').remove();
    if ($("#password").val() !== $("#retype-password").val()) {
      var fieldError = $('<label class="text-danger field-error">Password does not match</label>');
      fieldError.insertAfter($("#retype-password"));
      isValid = false;
    }
  }

  return isValid;
}

function saveUser() {
  if (validateUser()) {
    $.ajax({
      url: 'users/user-list/',
      type: 'POST',
      data: {
        "first_name": $("#first-name").val(),
        "last_name": $("#last-name").val(),
        "username": $("#username").val(),
        "password": $("#password").val(),
        "user_role": $("#user-role").val(),
        "email": $("#email").val(),
        "phone_number": $("#phone-number").val(),
        "department": $("#department").val(),
        'action': 'save'
      },
      success: function (data) {
        $("#new-user-modal-btn").click();
        setTimeout(() => {
          loadData('users/user-list/', 'GET', '');
        }, 500);
      },
      error: function (xhr, status, error) {
        alert('Error loading data: ' + error);
      }
    });
  }
}

function openNewUserModal() {
  $('.field-error').remove();
  $("#role-name").val("");
  $("#role-description").val("");
}

function closeNewUserModal() {
  $(".field-error").remove();
  $("#first-name").val("");
  $("#last-name").val("");
  $("#username").val("");
  $("#department").val("");
  $("#user-role").val("");
  $("#email").val("");
  $("#phone-number").val("");
  $("#retype-password").val("");
  $("#retype-password").val("");
  $("#user-role").val("");
}

function openEditUserModal(id) {
  $('.field-error').remove();
  $('#edit-user-dialog').modal('show');
  $.ajax({
    url: 'users/user-list/',
    type: 'GET',
    data: { 'id': id, 'action': 'edit' },
    success: function (data) {
      $('#edit-user-dialog').find('.modal-body').html(data.html);
    },
    error: function (xhr, status, error) {
      alert('Error loading data: ' + error);
    }
  });
}

function validateEditUser() {
  var isValid = true;
  $(".field-error").remove();

  if ($("#edit-first-name").val().length < 1) {
    errorMarker($("#edit-first-name"));
    isValid = false;
  }

  if ($("#edit-last-name").val().length < 1) {
    errorMarker($("#edit-last-name"));
    isValid = false;
  }

  if ($("#edit-department").val().length < 1) {
    errorMarker($("#edit-department"));
    isValid = false;
  }

  if ($("#edit-user-role").val().length < 1) {
    errorMarker($("#edit-user-role"));
    isValid = false;
  }

  if ($("#edit-email").val().length < 1) {
    errorMarker($("#edit-email"));
    isValid = false;
  }
  return isValid;
}

function closeEditUserModal() {
  $(".field-error").remove();
  $("#first-name").val("");
  $("#last-name").val("");
  $("#username").val("");
  $("#department").val("");
  $("#user-role").val("");
  $("#email").val("");
  $("#phone-number").val("");
  $("#retype-password").val("");
  $("#retype-password").val("");
  $("#user-role").val("");
}

function updateUser() {
  if (validateEditUser()) {
    $.ajax({
      url: 'users/user-list/',
      type: 'POST',
      data: {
        "first_name": $("#edit-first-name").val(),
        "last_name": $("#edit-last-name").val(),
        "user_role": $("#edit-user-role").val(),
        "email": $("#edit-email").val(),
        "phone_number": $("#edit-phone-number").val(),
        "department": $("#edit-department").val(),
        'action': 'edit'
      },
      success: function (data) {
        $("#edit-user-modal-btn").click();
        setTimeout(() => {
          loadData('users/user-list/', 'GET', '');
        }, 500);
      },
      error: function (xhr, status, error) {
        alert('Error loading data: ' + error);
      }
    });
  }
}