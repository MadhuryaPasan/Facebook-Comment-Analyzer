import React from "react"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "./ui/card"
import { Button } from "./ui/button"
import { Badge } from "./ui/badge"
import { ToggleGroup, ToggleGroupItem } from "./ui/toggle-group"
import { Tooltip, TooltipContent, TooltipTrigger } from "./ui/tooltip"
import { AspectRatio } from "./ui/aspect-ratio"
import Image from "next/image"
import { Separator } from "./ui/separator"
import { Dot, MessageCircle, MessageSquareShare } from "lucide-react"

const REACTION_META = [
  { key: "like", label: "Like", icon: "👍" },
  { key: "love", label: "Love", icon: "❤️" },
  { key: "care", label: "Care", icon: "🤗" },
  { key: "haha", label: "Haha", icon: "😂" },
  { key: "wow", label: "Wow", icon: "😮" },
  { key: "sad", label: "Sad", icon: "😢" },
  { key: "angry", label: "Angry", icon: "😡" },
] as const

export type ReactionKey = (typeof REACTION_META)[number]["key"]
export type ReactionCounts = Partial<Record<ReactionKey, number>>

export interface PostCardProps {
  message?: string
  imageUrl?: string
  isPostHidden?: boolean
  btnLable?: string
  reactions?: ReactionCounts
  selectedReaction?: readonly string[]
  onReactionChange?: (groupValue: string[]) => void
  onActionClick?: () => void
}

export const PostCard = ({
  message = "A practical talk on component APIs, accessibility, and shipping faster.A practical talk on component APIs, accessibility, and shipping faster.A practical talk on component APIs, accessibility, and shipping faster.A practical talk on component APIs, accessibility, and shipping faster.",
  imageUrl = "https://images.pexels.com/photos/39726485/pexels-photo-39726485.jpeg",
  // imageUrl = "",
  isPostHidden = false,
  btnLable = "View Post",
  // reactions = {},
  reactions = { like: 1111, love: 842, care: 120, haha: 310, wow: 54, sad: 12, angry: 5 },
  selectedReaction,
  onReactionChange,
  onActionClick,
}: PostCardProps) => {
  const formatCount = (count: number) => {
    const safeCount = Number.isFinite(count) && count > 0 ? count : 0
    return new Intl.NumberFormat("en", {
      notation: "compact",
      maximumFractionDigits: 1,
    }).format(safeCount)
  }

  return (
    <Card className="mx-auto w-full max-w-sm overflow-hidden pt-0 gap-1">
      <AspectRatio ratio={16 / 9} className="w-full max-w-sm rounded-lg bg-muted">
        {
          imageUrl ? (
            <Image
              src={imageUrl}
              alt="Post Attachment"
              fill
              className="rounded-lg object-cover dark:brightness-90"
            />
          ) :
            (
              <div className="flex h-full w-full flex-col items-center justify-center gap-1 px-1 py-2 opacity-50 text-lg">No image available</div>
            )
        }

      </AspectRatio>
      <CardHeader className="min-h-17 pt-3">
        <div className="">
          {isPostHidden ? (
            <Tooltip>
              <TooltipTrigger render={
                <Badge variant="outline" className="text-primary/60">Hidden</Badge>
              } />
              <TooltipContent>
                This post is not visible to the public
              </TooltipContent>
            </Tooltip>

          ) :

            <Tooltip>
              <TooltipTrigger render={
                <Badge variant="default" className="bg-green-400">Public</Badge>
              } />
              <TooltipContent>
                This post is visible to the public
              </TooltipContent>
            </Tooltip>
          }
        </div>
        <div className="line-clamp-2">{message}</div>
      </CardHeader>
      <CardContent className="">
        <ToggleGroup
          value={selectedReaction}
          onValueChange={onReactionChange}
          className="grid w-full grid-cols-7 gap-1 pt-2"
        >
          {REACTION_META.map((reaction) => {
            const count = reactions[reaction.key] ?? 0
            return (
              <div key={reaction.key}>
                <Tooltip>
                  <TooltipTrigger render={<ToggleGroupItem

                    value={reaction.key}
                    aria-label={`${reaction.label} (${count})`}
                    className="flex h-auto flex-col items-center  text-muted-foreground"
                  >
                    <span className="text-base leading-none" aria-hidden="true">
                      {reaction.icon}
                    </span>
                    <span className=" text-xs font-medium tabular-nums">
                      {formatCount(count)}
                    </span>
                  </ToggleGroupItem>} />
                  <TooltipContent>
                    <p>{`${reaction.label} (${count})`}</p>
                  </TooltipContent>
                </Tooltip>
              </div>
            )
          })}
        </ToggleGroup>

        <ToggleGroup className={"mx-auto w-fit text-muted-foreground pt-1 "}>
          <ToggleGroupItem className={"text-xs"}>
            <MessageCircle />{formatCount(2340)} Comments
          </ToggleGroupItem>
          <ToggleGroupItem className={"text-xs"}>
            <MessageSquareShare />{formatCount(186)} Shares
          </ToggleGroupItem>
        </ToggleGroup>
        <ToggleGroup className={"mx-auto w-fit text-muted-foreground gap-1 "} size={"sm"}>
          <ToggleGroupItem className={"text-green-400 p-0 text-[11px]"}>
            <Dot />Positive {formatCount(1420)}
          </ToggleGroupItem>
          <ToggleGroupItem className={" p-0 text-[11px]"}>
            <Dot />Neutral {formatCount(610)}
          </ToggleGroupItem>
          <ToggleGroupItem className={"text-red-400 p-0 text-[11px]"}>
            <Dot /> Negative {formatCount(310)}
          </ToggleGroupItem>
        </ToggleGroup>
      </CardContent>
      <CardFooter>


        <Button type="button" className="w-full" onClick={onActionClick}>
          {btnLable}
        </Button>
      </CardFooter>
    </Card>
  )
}



{/* <PostCard
  reactions={{ like: 1111, love: 842, care: 120, haha: 310, wow: 54, sad: 12, angry: 5 }}
  onActionClick={() => console.log("View event clicked")}
/> */}