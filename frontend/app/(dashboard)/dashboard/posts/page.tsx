import React from "react"
import { PostCard } from "@/components/post-card"

const ComponentName = () => {

  const postsList = [
    {
      postID: "4444",
      imageUrl: "https://images.pexels.com/photos/41049092/pexels-photo-41049092.jpeg",
      message: "hello world",
      isPostHidden: true,
      reactions: { like: 1111, love: 842, care: 120, haha: 310, wow: 54, sad: 12, angry: 5 },
      totalCommetnsCount: 500,
      postShareCount: 50,
      positiveComments: 50,
      neutralComments: 10,
      negativeComments: 100,
    },
    {
      postID: "4234",
      imageUrl: "https://images.pexels.com/photos/34469327/pexels-photo-34469327.jpeg",
      message: "hello world",
      isPostHidden: false,
      reactions: { like: 44, love: 88, care: 120, haha: 310, wow: 54, sad: 12, angry: 5 },
      totalCommetnsCount: 5,
      postShareCount: 8,
      positiveComments: 6,
      neutralComments: 10,
      negativeComments: 100,
    },
    {
      postID: "532",
      imageUrl: "https://images.pexels.com/photos/39429827/pexels-photo-39429827.jpeg",
      message: "hello world",
      isPostHidden: true,
      reactions: { like: 555, love: 842, care: 120, haha: 310, wow: 54, sad: 111, angry: 5 },
      totalCommetnsCount: 500,
      postShareCount: 50,
      positiveComments: 50,
      neutralComments: 10,
      negativeComments: 100,
    },
    {
      postID: "6632",
      imageUrl: "https://images.pexels.com/photos/41049092/pexels-photo-41049092.jpeg",
      message: "hello world",
      isPostHidden: true,
      reactions: { like: 1111, love: 842, care: 120, haha: 310, wow: 54, sad: 12, angry: 5 },
      totalCommetnsCount: 500,
      postShareCount: 50,
      positiveComments: 50,
      neutralComments: 10,
      negativeComments: 100,
    },
    {
      postID: "6423",
      imageUrl: "https://images.pexels.com/photos/34469327/pexels-photo-34469327.jpeg",
      message: "hello world",
      isPostHidden: false,
      reactions: { like: 44, love: 88, care: 120, haha: 310, wow: 54, sad: 12, angry: 5 },
      totalCommetnsCount: 5,
      postShareCount: 8,
      positiveComments: 6,
      neutralComments: 10,
      negativeComments: 100,
    },
    {
      postID: "1234",
      imageUrl: "https://images.pexels.com/photos/39429827/pexels-photo-39429827.jpeg",
      message: "hello world",
      isPostHidden: true,
      reactions: { like: 555, love: 842, care: 120, haha: 310, wow: 54, sad: 111, angry: 5 },
      totalCommetnsCount: 500,
      postShareCount: 50,
      positiveComments: 50,
      neutralComments: 10,
      negativeComments: 100,
    },
  ]

  return (
    <div>

      <section aria-label="Posts feed" className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">

          {postsList.map((post, index) => (
            < PostCard
              key={index}
              {...post}
            />
          ))}
        </div>
      </section>
    </div>
  )
}

export default ComponentName
