import { Search, Heart, MessageCircle, CircleUser } from "lucide-react"

export const AUTHENTICATED_NAV_ITEMS = [
  { href: "/search", label: "Search", icon: Search },
  { href: "/products", label: "My Products", icon: Heart },
  { href: "/chatbot", label: "Chatbot", icon: MessageCircle },
  { href: "/account", label: "Account", icon: CircleUser },
] as const
