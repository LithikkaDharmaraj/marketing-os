import { z } from "zod";

export const contactSchema = z.object({
  full_name: z.string().optional(),
  email: z.string().email("Invalid email").optional().or(z.literal("")),
  phone: z.string().optional(),
  linkedin_url: z.string().url("Invalid URL").optional().or(z.literal("")),
  job_title: z.string().optional(),
  contact_type: z.string().default("general"),
  is_founder: z.boolean().default(false),
  is_primary: z.boolean().default(false),
});

export const companyInfoSchema = z.object({
  company_name: z.string().min(2, "Company name required"),
  website_url: z.string().min(3, "Website URL required"),
  industry: z.string().min(2, "Industry required"),
  sub_industry: z.string().optional(),
  company_size: z.string().min(1, "Company size required"),
  geography: z.string().min(2, "Geography required"),
  business_model: z.string().min(1, "Business model required"),
  linkedin_url: z.string().url("Invalid URL").optional().or(z.literal("")),
  annual_revenue_range: z.string().optional(),
});

export const productSchema = z.object({
  product_type: z.string().min(1, "Product type required"),
  product_name: z.string().optional(),
  product_description: z.string().optional(),
  services_products: z.string().optional(),
  pricing_range: z.string().optional(),
  core_features: z.array(z.string()).default([]),
  differentiators: z.array(z.string()).default([]),
  problems_solved: z.array(z.string()).default([]),
});

export const goalsSchema = z.object({
  target_market: z.string().optional(),
  target_segments: z.array(z.string()).default([]),
  goals: z.array(z.string()).default([]),
});

export const intakeSchema = companyInfoSchema
  .merge(productSchema)
  .merge(goalsSchema)
  .extend({
    competitors: z.array(z.string()).default([]),
    contacts: z.array(contactSchema).default([]),
    tenant_id: z.string().uuid(),
  });

export type IntakeFormValues = z.infer<typeof intakeSchema>;
