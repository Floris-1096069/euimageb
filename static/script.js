// Toggle reply form visibility
function toggleReplyForm(postId) {
  const form = document.getElementById(`reply-form-${postId}`);
  if (form) {
    if (form.style.display === 'none') {
      form.style.display = 'block';
    } else {
      form.style.display = 'none';
    }
  }
}

// Image preview for all forms (post and reply)
document.addEventListener('DOMContentLoaded', function() {
  // Image preview logic (does NOT trigger HTMX)
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

  // Reset post form ONLY after successful submission
  const postForm = document.getElementById('post-form');
  if (postForm) {
    postForm.addEventListener('htmx:afterRequest', function(evt) {
      // Only reset if the request was a POST and successful
      if (evt.detail.requestConfig.method === 'POST' && evt.detail.successful) {
        postForm.reset();
        const preview = postForm.querySelector('img');
        if (preview) preview.remove();
      }
    });
  }

  // Reset reply forms ONLY after successful submission
  document.querySelectorAll('[id^="reply-form-"]').forEach(form => {
    form.addEventListener('htmx:afterRequest', function(evt) {
      // Only reset if the request was a POST and successful
      if (evt.detail.requestConfig.method === 'POST' && evt.detail.successful) {
        form.reset();
        const preview = form.querySelector('img');
        if (preview) preview.remove();
        form.style.display = 'none';  // Hide after submission
      }
    });
  });
});