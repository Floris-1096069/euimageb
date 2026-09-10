window.toggleReplyForm = function(postId) {
  const form = document.getElementById(`reply-form-${postId}`);
  if (form) {
    if (form.style.display === 'none') {
      form.style.display = 'block';
    } else {
      form.style.display = 'none';
    }
  }
};

window.toggleBoardForm = function() {
  const form = document.getElementById(`board-form`);
  if (form) {
    if (form.style.display === 'none') {
      form.style.display = 'block';
    } else {
      form.style.display = 'none';
    }
  }
};

document.addEventListener('DOMContentLoaded', function() {
  //image preview for all forms
  document.querySelectorAll('input[type="file"]').forEach(input => {
    input.addEventListener('change', function(e) {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
          const preview = document.createElement('img');
          preview.src = e.target.result;
          preview.style.maxWidth = '200px';
          preview.style.maxHeight = '200px';
          preview.style.marginTop = '10px';
          input.parentNode.insertBefore(preview, input.nextSibling);
        };
        reader.readAsDataURL(file);
      }
    });
  });

  //reset post form after successful submission
  const postForm = document.getElementById('post-form');
  if (postForm) {
    postForm.addEventListener('htmx:afterRequest', function(evt) {
      if (evt.detail.successful && evt.target.id === 'post-form') {
        postForm.reset();
        const preview = postForm.querySelector('img');
        if (preview) preview.remove();
      }
    });
  }

  //reset board form after succesful submission
  document.addEventListener('htmx:afterRequest', function (evt){
    if (evt.detail.successful && evt.target.id && evt.target.id.startsWith('board-form')) {
      const form = evt.target;
      form.reset()
    }
  })

  //reset reply forms after successful submission
  document.addEventListener('htmx:afterRequest', function(evt) {
    if (evt.detail.successful && evt.target.id && evt.target.id.startsWith('reply-form-')) {
      const form = evt.target;
      form.reset();
      const preview = form.querySelector('img');
      if (preview) preview.remove();
      form.style.display = 'none';
    }
  });
});