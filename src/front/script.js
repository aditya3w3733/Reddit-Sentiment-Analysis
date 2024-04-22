document.addEventListener('DOMContentLoaded', function() {
    const apiUrl = 'https://463s3i2zgk.execute-api.ap-south-1.amazonaws.com/test/posts'; 
    const postsContainer = document.querySelector('.posts-container');

    function createPostCard(post) {
    if (post.article_summary == null || post.comment_summary == null) {
        return null;
    }

    const card = document.createElement('article');
    card.className = 'card';
    card.innerHTML = `
        <div class="post-date">Posted on: ${post.post_creation_date || "date not available"} </div>
        <br>
        <h2>${post.post_title}</h2> 
        <p class="article-summary">${post.article_summary}</p> 
        <div class="comment-card">
            <h3>Comments Summary</h3>
            <p>${post.comment_summary}</p>
        </div>
        <div class="links">
            <br>
            <a href="${post.news_link || "#"}" target="_blank">Go to original article</a>
            <br>
            <a href="${post.comments_link || "#"}" target="_blank">Go to comments</a>
        </div>
    `;
    return card;
}


    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            if (!data || data.length === 0) {
                throw new Error('No posts found');
            }
            data.forEach(post => {
                const postCard = createPostCard(post);
                if (postCard) {
                    postsContainer.appendChild(postCard);
                }
            });
        })
        .catch(error => {
            console.error('Error fetching posts:', error);
            postsContainer.innerHTML = '<p class="error-message">Failed to load posts. Please try again later.</p>';
        });
});
