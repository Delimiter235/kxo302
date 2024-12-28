document.addEventListener("DOMContentLoaded", function() {
    // 为所有带有类名 like-btn 的按钮添加点击事件
    document.querySelectorAll('.like-btn').forEach(button => {
        button.addEventListener('click', function() {
            const reviewId = this.getAttribute('data-review-id');  // 获取当前评论的 ID
            
            // 发送 POST 请求，更新点赞数
            fetch(`/like_comment/${reviewId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ review_id: reviewId })
            })
            .then(response => response.json())
            .then(data => {
                // 如果返回错误，提示用户
                if (data.error) {
                    alert(data.error);  
                    return;
                }

                const likeCountElement = this.previousElementSibling.querySelector('.like-count');
                likeCountElement.textContent = data.new_like_count;

                this.disabled = true;
                this.textContent = "Liked";
            })
            .catch(error => {
                console.error('Error:', error); 
            });
        });
    });
});

