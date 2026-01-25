export interface PathDetail {
  from_id: string
  to_id: string
  relationship: string
}

export interface KinshipResponse {
  relationship_path: string
  title: string
  reverse_title: string
  generation_diff: number
  is_direct: boolean
  path_details: PathDetail[]
}

export interface KinshipCalculateRequest {
  family_tree_id: number
  from_member_id: string
  to_member_id: string
  dialect?: string
}
