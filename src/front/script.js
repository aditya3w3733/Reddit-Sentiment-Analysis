document.addEventListener('DOMContentLoaded', function() {
    const apiUrl = 'https://your-aws-region/test/posts'; //enter your API Gateways's REST API endpoint here
    const postsContainer = document.querySelector('.posts-container');
    const flairSidebar = document.getElementById('flair-sidebar');

    function createPostCard(post) {
    if (post.article_summary == null || post.comment_summary == null) {
        //console.log('Skipping post due to missing summary:', post);   // for debugging
        return null;
    }


    const card = document.createElement('article');
    card.className = 'card';
    card.dataset.flair = post.flair;
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


function clearActiveFlair() {
    document.querySelectorAll('.flair-tab').forEach(tab => {
        tab.classList.remove('active');
    });
}


// function to set a flair tab as active
function setActiveFlair(flair) {
    clearActiveFlair();
    const flairTab = document.querySelector(`.flair-tab[data-flair="${flair}"]`); // Make sure this matches your flair button selector

    if (flairTab) {
        flairTab.classList.add('active');

    }
}



    //function to create a flair tab
    function createFlairTab(flair) {
    const tab = document.createElement('button');
    tab.textContent = flair;
    tab.dataset.flair = flair; //set a data attribute for the flair
    tab.className = 'flair-tab';
    tab.onclick = function() {
        setActiveFlair(flair); //set active flair
        filterPostsByFlair(flair);
    };
    return tab;
}


function clearActiveFlair() {
    document.querySelectorAll('.flair-tab').forEach(tab => {
        tab.classList.remove('active');
    });
}

    //function to filter by flair
    function filterPostsByFlair(flair) {
    const allCards = document.querySelectorAll('.card');
    allCards.forEach(card => {
        if (flair === 'All' || card.dataset.flair === flair) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
}


//fetch posts and populate the UI
fetch(apiUrl)
    .then(response => response.json())
    .then(data => {
        const { posts, flairs: fetchedFlairs } = data;

        //process fetched flairs
        let displayedFlairs = new Set(['All']);    //start with 'All'


        //create flair tabs
        fetchedFlairs.forEach(flair => {
            displayedFlairs.add(flair);
            const flairTab = createFlairTab(flair);
            flairSidebar.appendChild(flairTab);
        });

        // append 'All' tab to the beginning of flairSidebar
        const allFlairTab = createFlairTab('All');
        allFlairTab.classList.add('active');   // set 'All' = active tab on page load
        flairSidebar.prepend(allFlairTab);
        setActiveFlair('All');


        // process posts cards 
        posts.forEach(post => {
            const postCard = createPostCard(post);
            if (postCard) {
                postsContainer.appendChild(postCard);
            }
        });

        // initially show all posts
        filterPostsByFlair('All');
    })
    .catch(error => {
        console.error('Error fetching posts:', error);
        postsContainer.innerHTML = '<p class="error-message">Failed to load posts. Please try again later.</p>';
    });
});
