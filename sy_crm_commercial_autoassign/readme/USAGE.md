To use this module, you need to:

1. Go to **CRM > Configuration > Commercial Auto Assignments**.
2. Create a new commercial auto assignment and configure the following fields:
   - **Name**: Name of the assignment.
   - **Salesperson**: User to be automatically assigned to contacts.
   - **ZIP Codes**: Select one or more ZIP codes associated with the salesperson.
   - **Company**: Company to which the assignment applies.
   - **Notes**: Additional information about the assignment.
3. Go to **Contacts** and create or edit a contact.
4. Set the contact's **ZIP Code**. If it matches a configured ZIP code, the corresponding salesperson will be automatically assigned.
5. Enable **Keep Salesperson** in the **Sales & Purchase** tab to prevent automatic reassignment when the contact's ZIP code changes.

**Additional information:**

- Each ZIP code can only be assigned to one commercial auto assignment per company.
- When a contact's ZIP code changes, the salesperson is automatically recalculated unless **Keep Salesperson** is enabled.
- If no matching ZIP code is found, the existing salesperson is preserved.
- Disabling **Keep Salesperson** triggers a new automatic assignment based on the contact's current ZIP code.
- Changes to the salesperson and ZIP codes in the assignment configuration are tracked in the chatter.
