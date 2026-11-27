"use client"

import React from "react"
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "./ui/card"
import { Button } from "./ui/button"
import { Badge } from "./ui/badge"
import { ToggleGroup, ToggleGroupItem } from "./ui/toggle-group"
import { Tooltip, TooltipContent, TooltipTrigger } from "./ui/tooltip"
import { AspectRatio } from "./ui/aspect-ratio"
import Image from "next/image"
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
  postID?: string
  message?: string
  imageUrl?: string
  isPostHidden?: boolean
  btnLabel?: string
  btnLable?: string
  reactions?: ReactionCounts
  selectedReaction?: string[]
  positiveComments?: number
  neutralComments?: number
  negativeComments?: number
  totalCommentsCount?: number
  totalCommetnsCount?: number
  postShareCount?: number
  selectedSentiment?: string[]
  // onActionClick?: () => void
}

const toSafeCount = (value?: number): number => {
  if (typeof value !== "number" || !Number.isFinite(value) || value < 0) {
    return 0
  }
  return value
}

export const PostCard = ({
  postID,
  message = "",
  imageUrl,
  isPostHidden = true,
  btnLabel,
  btnLable = "View Post",
  reactions = { like: 0, love: 0, care: 0, haha: 0, wow: 0, sad: 0, angry: 0 },
  totalCommentsCount,
  totalCommetnsCount = 0,
  postShareCount = 0,
  selectedReaction,
  selectedSentiment,
  positiveComments = 0,
  neutralComments = 0,
  negativeComments = 0,
  // onActionClick

}: PostCardProps) => {
  const resolvedButtonLabel = btnLabel ?? btnLable
  const resolvedCommentsCount = toSafeCount(totalCommentsCount ?? totalCommetnsCount)
  const resolvedSharesCount = toSafeCount(postShareCount)

  const formatCount = (count: number) => {
    const safeCount = toSafeCount(count)
    return new Intl.NumberFormat("en", {
      notation: "compact",
      maximumFractionDigits: 1,
    }).format(safeCount)
  }

  const [imgError, setImgError] = React.useState(false)

  React.useEffect(() => {
    setImgError(false)
  }, [imageUrl])

  const totalReactions = REACTION_META.reduce(
    (sum, { key }) => sum + toSafeCount(reactions[key]),
    0
  )

  const safePositive = toSafeCount(positiveComments)
  const safeNeutral = toSafeCount(neutralComments)
  const safeNegative = toSafeCount(negativeComments)
  const sentimentTotal = safePositive + safeNeutral + safeNegative
  const denominator = sentimentTotal || 1

  const positivePct = (safePositive / denominator) * 100
  const neutralPct = (safeNeutral / denominator) * 100
  const negativePct = (safeNegative / denominator) * 100

  return (
    <Card
      data-post-id={postID}
      className="mx-auto w-full max-w-sm gap-1 overflow-hidden pt-0 shadow-lg"
    >
      <AspectRatio ratio={16 / 9} className="w-full max-w-sm rounded-lg bg-muted">
        <div className="absolute top-2 right-2 z-10">
          {isPostHidden ? (
            <Tooltip>
              <TooltipTrigger
                render={
                  <Badge variant="default" className="p-3">
                    <Dot className="scale-500 text-slate-500" />
                    Hidden
                  </Badge>
                }
              />
              <TooltipContent>
                This post is not visible to the public
              </TooltipContent>
            </Tooltip>
          ) : (
            <Tooltip>
              <TooltipTrigger
                render={
                  <Badge variant="default" className="p-3">
                    <Dot className="scale-500 text-green-500" />
                    Public
                  </Badge>
                }
              />
              <TooltipContent>
                This post is visible to the public
              </TooltipContent>
            </Tooltip>
          )}
        </div>

        {imageUrl && !imgError ? (
          <Image
            src={imageUrl}
            alt="Post attachment"
            fill
            sizes="(max-width: 640px) 100vw, 384px"
            unoptimized
            onError={() => setImgError(true)}
            className="rounded-lg object-cover dark:brightness-90"
          />
        ) : (
          <div className="flex h-full w-full flex-col items-center justify-center gap-1 px-1 py-2 text-muted-foreground opacity-50">
            No image available
          </div>
        )}
      </AspectRatio>

      <CardHeader className="min-h-17 pt-3">
        <div className="line-clamp-2">{message.trim() || "No message available!"}</div>
      </CardHeader>

      <CardContent>
        <div className="flex w-full items-center justify-between text-xs opacity-45">
          <div>REACTIONS</div>
          <div>{formatCount(totalReactions)}</div>
        </div>

        <ToggleGroup
          value={selectedReaction}
          className="grid w-full grid-cols-7 gap-1 pt-4"
        >
          {REACTION_META.map((reaction) => {
            const count = toSafeCount(reactions[reaction.key])
            return (
              <div key={reaction.key}>
                <Tooltip>
                  <TooltipTrigger
                    render={
                      <ToggleGroupItem
                        value={reaction.key}
                        aria-label={`${reaction.label} (${count})`}
                        className="flex h-auto flex-col items-center text-muted-foreground"
                      >
                        <span className="text-base leading-none" aria-hidden="true">
                          {reaction.icon}
                        </span>
                        <span className="text-xs font-medium tabular-nums">
                          {formatCount(count)}
                        </span>
                      </ToggleGroupItem>
                    }
                  />
                  <TooltipContent>
                    <p>{`${reaction.label} (${count})`}</p>
                  </TooltipContent>
                </Tooltip>
              </div>
            )
          })}
        </ToggleGroup>

        <div className="flex w-full items-center justify-between pt-2 text-xs text-muted-foreground">
          <div className="inline-flex items-center gap-1.5 px-2 py-1">
            <MessageCircle className="size-4" />
            <span>{formatCount(resolvedCommentsCount)} Comments</span>
          </div>
          <div className="inline-flex items-center gap-1.5 px-2 py-1">
            <MessageSquareShare className="size-4" />
            <span>{formatCount(resolvedSharesCount)} Shares</span>
          </div>
        </div>

        <section className="space-y-1.5 pt-3">
          <div className="text-xs opacity-45">COMMENT SENTIMENT</div>

          <div className="flex h-2.5 w-full gap-1 overflow-hidden rounded-full border bg-muted">
            {safePositive > 0 && (
              <Tooltip>
                <TooltipTrigger
                  render={
                    <div
                      style={{ width: `${positivePct}%` }}
                      className="h-full bg-green-500 transition-all duration-300"
                    />
                  }
                />
                <TooltipContent>
                  {safePositive} positive comments
                </TooltipContent>
              </Tooltip>
            )}
            {safeNeutral > 0 && (
              <Tooltip>
                <TooltipTrigger
                  render={
                    <div
                      style={{ width: `${neutralPct}%` }}
                      className="h-full bg-slate-400 transition-all duration-300"
                    />
                  }
                />
                <TooltipContent>
                  {safeNeutral} neutral comments
                </TooltipContent>
              </Tooltip>
            )}
            {safeNegative > 0 && (
              <Tooltip>
                <TooltipTrigger
                  render={
                    <div
                      style={{ width: `${negativePct}%` }}
                      className="h-full bg-red-500 transition-all duration-300"
                    />
                  }
                />
                <TooltipContent>
                  {safeNegative} negative comments
                </TooltipContent>
              </Tooltip>
            )}
          </div>

          <ToggleGroup
            value={selectedSentiment}
            className="flex w-full items-center justify-between gap-2 text-muted-foreground"
            size="sm"
          >
            <ToggleGroupItem
              value="positive"
              className="flex h-auto flex-1 flex-col items-center gap-0.5 py-1.5"
            >
              <div className="flex items-center gap-1">
                <span className="size-2 rounded-full bg-green-500" />
                <span className="text-xs">Positive</span>
              </div>
              <div className="text-sm font-medium text-foreground">
                {formatCount(safePositive)}
              </div>
              <span className="text-xs">{positivePct.toFixed(2)}%</span>
            </ToggleGroupItem>

            <ToggleGroupItem
              value="neutral"
              className="flex h-auto flex-1 flex-col items-center gap-0.5 py-1.5"
            >
              <div className="flex items-center gap-1">
                <span className="size-2 rounded-full bg-slate-400" />
                <span className="text-xs">Neutral</span>
              </div>
              <div className="text-sm font-medium text-foreground">
                {formatCount(safeNeutral)}
              </div>
              <span className="text-xs">{neutralPct.toFixed(2)}%</span>
            </ToggleGroupItem>

            <ToggleGroupItem
              value="negative"
              className="flex h-auto flex-1 flex-col items-center gap-0.5 py-1.5"
            >
              <div className="flex items-center gap-1">
                <span className="size-2 rounded-full bg-red-500" />
                <span className="text-xs">Negative</span>
              </div>
              <div className="text-sm font-medium text-foreground">
                {formatCount(safeNegative)}
              </div>
              <span className="text-xs">{negativePct.toFixed(2)}%</span>
            </ToggleGroupItem>
          </ToggleGroup>
        </section>
      </CardContent>

      <CardFooter>
        <Button type="button" className="w-full" onClick={()=>{console.log(postID)}}>
          {resolvedButtonLabel}
        </Button>
      </CardFooter>
    </Card>
  )
}